from infinity_addressing.addresser import AddressSpace
from infinity_addressing.addresser import get_address_type
from infinity_protobuf.user_pb2 import UserContainer
from infinity_protobuf.record_pb2 import RecordContainer


CONTAINERS = {
    AddressSpace.USER: UserContainer,
    AddressSpace.RECORD: RecordContainer
}


def deserialize_data(address, data):
    """Deserializes state data by type based on the address structure and
    returns it as a dictionary with the associated data type

    Args:
        address (str): The state address of the container
        data (str): String containing the serialized state data
    """
    data_type = get_address_type(address)

    if data_type == AddressSpace.OTHER_FAMILY:
        return []

    try:
        container = CONTAINERS[data_type]
    except KeyError:
        raise TypeError('Unknown data type: {}'.format(data_type))

    entries = _parse_proto(container, data).entries
    return data_type, [_convert_proto_to_dict(pb) for pb in entries]


def _parse_proto(proto_class, data):
    deserialized = proto_class()
    deserialized.ParseFromString(data)
    return deserialized


def _convert_proto_to_dict(proto):
    result = {}

    for field in proto.DESCRIPTOR.fields:
        key = field.name
        value = getattr(proto, key)

        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                result[key] = [_convert_proto_to_dict(p) for p in value]
            else:
                result[key] = _convert_proto_to_dict(value)

        elif field.type == field.TYPE_ENUM:
            number = int(value)
            name = field.enum_type.values_by_number.get(number).name
            result[key] = name

        else:
            result[key] = value

    return result
