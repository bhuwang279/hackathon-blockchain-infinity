from sawtooth_sdk.processor.exceptions import InvalidTransaction
from infinity_protobuf import payload_pb2


class InfinityPayload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.InfinityPayload()
        self._transaction.ParseFromString(payload)

    @property
    def action(self):
        return self._transaction.action

    @property
    def data(self):
        if self._transaction.HasField('create_user') and \
            self._transaction.action == \
                payload_pb2.InfinityPayload.CREATE_USER:
            return self._transaction.create_user

        if self._transaction.HasField('create_record') and \
            self._transaction.action == \
                payload_pb2.InfinityPayload.CREATE_RECORD:
            return self._transaction.create_record

        if self._transaction.HasField('transfer_record') and \
            self._transaction.action == \
                payload_pb2.InfinityPayload.TRANSFER_RECORD:
            return self._transaction.transfer_record

        if self._transaction.HasField('update_record_location') and \
            self._transaction.action == \
                payload_pb2.InfinityPayload.UPDATE_RECORD_LOCATION:
            return self._transaction.update_record_location
        if self._transaction.HasField('update_record_for_sale') and \
            self._transaction.action == \
                payload_pb2.InfinityPayload.UPDATE_RECORD_FOR_SALE:
            return self._transaction.update_record_for_sale

        raise InvalidTransaction('Action does not match payload data')

    @property
    def timestamp(self):
        return self._transaction.timestamp

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(
            ('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))