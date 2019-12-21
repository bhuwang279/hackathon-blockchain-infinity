import datetime
from json.decoder import JSONDecodeError
import logging
import time

from aiohttp.web import json_response
import bcrypt
from Crypto.Cipher import AES
from itsdangerous import BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from infinity_rest_api.errors import ApiBadRequest
from infinity_rest_api.errors import ApiNotFound
from infinity_rest_api.errors import ApiUnauthorized


LOGGER = logging.getLogger(__name__)


class RouteHandler(object):
    def __init__(self, loop, messenger, database):
        self._loop = loop
        self._messenger = messenger
        self._database = database

    async def authenticate(self, request):
        body = await decode_request(request)
        required_fields = ['public_key', 'password']
        validate_fields(required_fields, body)

        password = bytes(body.get('password'), 'utf-8')

        auth_info = await self._database.fetch_auth_resource(
            body.get('public_key'))
        if auth_info is None:
            raise ApiUnauthorized('No user with that public key exists')

        hashed_password = auth_info.get('hashed_password')
        if not bcrypt.checkpw(password, bytes.fromhex(hashed_password)):
            raise ApiUnauthorized('Incorrect public key or password')

        token = generate_auth_token(
            request.app['secret_key'], body.get('public_key'))

        return json_response({'authorization': token})

    async def create_user(self, request):
        body = await decode_request(request)
        required_fields = ['name', 'password','role']
        validate_fields(required_fields, body)

        public_key, private_key = self._messenger.get_new_key_pair()

        await self._messenger.send_create_user_transaction(
            private_key=private_key,
            name=body.get('name'),
            role=body.get('role'),
            timestamp=get_time())

        encrypted_private_key = encrypt_private_key(
            request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))

        await self._database.create_auth_entry(
            public_key, encrypted_private_key, hashed_password,body.get('role'))

        token = generate_auth_token(
            request.app['secret_key'], public_key)

        return json_response({'authorization': token})

    async def list_users(self, _request):
        user_list = await self._database.fetch_all_user_resources()
        return json_response(user_list)

    async def fetch_user(self, request):
        public_key = request.match_info.get('user_id', '')
        user = await self._database.fetch_user_resource(public_key)
        if user is None:
            raise ApiNotFound(
                'user with public key {} was not found'.format(public_key))
        return json_response(user)

    async def create_record(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['latitude', 'longitude', 'record_id', 'name', 'price', 'isForSale']
        validate_fields(required_fields, body)

        await self._messenger.send_create_record_transaction(
            private_key=private_key,
            latitude=body.get('latitude'),
            longitude=body.get('longitude'),
            record_id=body.get('record_id'),
            name=body.get('name'),
            price= body.get('price'),
            isForSale=body.get('isForSale'),
            imageUrl=body.get('imageUrl'),
            timestamp=get_time())

        return json_response(
            {'data': 'Create record transaction submitted'})

    async def list_records(self, _request):
        record_list = await self._database.fetch_all_record_resources()
        return json_response(record_list)

    async def fetch_record(self, request):
        record_id = request.match_info.get('record_id', '')
        record = await self._database.fetch_record_resource(record_id)
        if record is None:
            raise ApiNotFound(
                'Record with the record id '
                '{} was not found'.format(record_id))
        return json_response(record)

    async def transfer_record(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['receiving_user']
        validate_fields(required_fields, body)

        record_id = request.match_info.get('record_id', '')

        await self._messenger.send_transfer_record_transaction(
            private_key=private_key,
            receiving_user=body['receiving_user'],
            record_id=record_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Transfer record transaction submitted'})

    async def update_record_location(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['latitude', 'longitude']
        validate_fields(required_fields, body)

        record_id = request.match_info.get('record_id', '')

        await self._messenger.send_update_record_location_transaction(
            private_key=private_key,
            latitude=body['latitude'],
            longitude=body['longitude'],
            record_id=record_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Update record transaction submitted'})
    async def update_record_for_sale(self, request):
        private_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['isForSale']
        validate_fields(required_fields, body)

        record_id = request.match_info.get('record_id', '')

        await self._messenger.send_update_record_for_sale_transaction(
            private_key=private_key,
            isForSale=body['isForSale'],
            record_id=record_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Update record transaction submitted'})


    async def _authorize(self, request):
        token = request.headers.get('AUTHORIZATION')
        if token is None:
            raise ApiUnauthorized('No auth token provided')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()
        try:
            token_dict = deserialize_auth_token(request.app['secret_key'],
                                                token)
        except BadSignature:
            raise ApiUnauthorized('Invalid auth token')
        public_key = token_dict.get('public_key')

        auth_resource = await self._database.fetch_auth_resource(public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token is not associated with an user')
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key'])


async def decode_request(request):
    try:
        return await request.json()
    except JSONDecodeError:
        raise ApiBadRequest('Improper JSON format')


def validate_fields(required_fields, body):
    for field in required_fields:
        if body.get(field) is None:
            raise ApiBadRequest(
                "'{}' parameter is required".format(field))


def encrypt_private_key(aes_key, public_key, private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.encrypt(private_key)


def decrypt_private_key(aes_key, public_key, encrypted_private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    private_key = cipher.decrypt(bytes.fromhex(encrypted_private_key))
    return private_key


def hash_password(password):
    return bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())


def get_time():
    dts = datetime.datetime.utcnow()
    return round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)


def generate_auth_token(secret_key, public_key):
    serializer = Serializer(secret_key)
    token = serializer.dumps({'public_key': public_key})
    return token.decode('ascii')


def deserialize_auth_token(secret_key, token):
    serializer = Serializer(secret_key)
    return serializer.loads(token)
