import enum
import hashlib


FAMILY_NAME = 'infinity'
FAMILY_VERSION = '0.1'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]
USER_PREFIX = '00'
RECORD_PREFIX = '01'


@enum.unique
class AddressSpace(enum.IntEnum):
    USER = 0
    RECORD = 1

    OTHER_FAMILY = 100


def get_user_address(public_key):
    return NAMESPACE + USER_PREFIX + hashlib.sha512(
        public_key.encode('utf-8')).hexdigest()[:62]


def get_record_address(record_id):
    return NAMESPACE + RECORD_PREFIX + hashlib.sha512(
        record_id.encode('utf-8')).hexdigest()[:62]


def get_address_type(address):
    if address[:len(NAMESPACE)] != NAMESPACE:
        return AddressSpace.OTHER_FAMILY

    infix = address[6:8]

    if infix == '00':
        return AddressSpace.USER
    if infix == '01':
        return AddressSpace.RECORD

    return AddressSpace.OTHER_FAMILY
