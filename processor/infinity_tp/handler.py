
import datetime
import time

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction


from infinity_addressing import addresser

from infinity_protobuf import payload_pb2
from infinity_tp.payload import InfinityPayload
from infinity_tp.state import InfinityState


SYNC_TOLERANCE = 60 * 5
MAX_LAT = 90 * 1e6
MIN_LAT = -90 * 1e6
MAX_LNG = 180 * 1e6
MIN_LNG = -180 * 1e6


class InfinityHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def family_versions(self):
        return [addresser.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [addresser.NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        payload = InfinityPayload(transaction.payload)
        state = InfinityState(context)

        _validate_timestamp(payload.timestamp)

        if payload.action == payload_pb2.InfinityPayload.CREATE_USER:
            _create_user(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.InfinityPayload.CREATE_RECORD:
            _create_record(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.InfinityPayload.TRANSFER_RECORD:
            _transfer_record(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.InfinityPayload.UPDATE_RECORD_LOCATION:
            _update_record_location(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.InfinityPayload.UPDATE_RECORD_FOR_SALE:
            _update_record_is_for_sale(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.InfinityPayload.UPDATE_RECORD_STOLEN:
            _update_record_stolen(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        else:
            raise InvalidTransaction('Unhandled action')


def _create_user(state, public_key, payload):

    if state.get_user(public_key):
        raise InvalidTransaction('User with the public key {} already '
                                 'exists'.format(public_key))
    state.set_user(
        public_key=public_key,
        name=payload.data.name,
        role=payload.data.role,
        timestamp=payload.timestamp)


def _create_record(state, public_key, payload):
    print(payload)
    print("Price")
    print(payload.data.price)
    if state.get_user(public_key) is None:
        raise InvalidTransaction('User with the public key {} does '
                                 'not exist'.format(public_key))

    if payload.data.record_id == '':
        raise InvalidTransaction('No record ID provided')

    if state.get_record(payload.data.record_id):
        raise InvalidTransaction('Identifier {} belongs to an existing '
                                 'record'.format(payload.data.record_id))

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.set_record(
        public_key=public_key,
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        name=payload.data.name,
        imageUrl=payload.data.imageUrl,
        price=payload.data.price,
        isForSale=payload.data.isForSale,
        timestamp=payload.timestamp)


def _transfer_record(state, public_key, payload):
    if state.get_user(payload.data.receiving_agent) is None:
        raise InvalidTransaction(
            'User with the public key {} does '
            'not exist'.format(payload.data.receiving_agent))

    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    state.transfer_record(
        receiving_agent=payload.data.receiving_agent,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _update_record_location(state, public_key, payload):
    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.update_record_location(
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)

def _update_record_is_for_sale(state, public_key, payload):
    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key, record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record'
        )
    state.update_record_is_for_sale(
        record_id=payload.data.record_id,
        isForSale=payload.data.isForSale,
        timestamp=payload.timestamp,
    )


def _update_record_stolen(state, public_key, payload):
    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key, record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record'
        )
    state.update_record_is_stolen(
        record_id=payload.data.record_id,
        is_stolen=payload.data.is_stolen,
        timestamp=payload.timestamp,
    )


def _validate_record_owner(signer_public_key, record):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the record
    """
    latest_owner = max(record.owners, key=lambda obj: obj.timestamp).user_id
    return latest_owner == signer_public_key


def _validate_latlng(latitude, longitude):
    if not MIN_LAT <= latitude <= MAX_LAT:
        raise InvalidTransaction('Latitude must be between -90 and 90. '
                                 'Got {}'.format(latitude/1e6))
    if not MIN_LNG <= longitude <= MAX_LNG:
        raise InvalidTransaction('Longitude must be between -180 and 180. '
                                 'Got {}'.format(longitude/1e6))


def _validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond/1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.format(
                timestamp, current_time, SYNC_TOLERANCE))
