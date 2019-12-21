import hashlib

from sawtooth_rest_api.protobuf import batch_pb2
from sawtooth_rest_api.protobuf import transaction_pb2

from infinity_addressing import addresser

from infinity_protobuf import payload_pb2


def make_create_user_transaction(transaction_signer,
                                 batch_signer,
                                 name,
                                 role,
                                 timestamp):
    """Make a CreateUserAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        name (str): The agent's name
        role(str): The role of user, accepted values [Admin, Creator, User, Querier]
        timestamp (int): Unix UTC timestamp of when the agent is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch

    """

    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())

    inputs = [user_address]

    outputs = [user_address]

    action = payload_pb2.CreateUserAction(name=name, role=role)

    payload = payload_pb2.InfinityPayload(
        action=payload_pb2.InfinityPayload.CREATE_USER,
        create_user=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_record_transaction(transaction_signer,
                                   batch_signer,
                                   latitude,
                                   longitude,
                                   record_id,
                                   imageUrl,
                                   name,
                                   price,
                                   isForSale,
                                   timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        latitude (int): Initial latitude of the record
        longitude (int): Initial latitude of the record
        record_id (str): Unique ID of the record
        imageUrl (str): ImageUrl of the record
        price (str): Price of record if any
        isForSale(bool): bool flag if product is for sale
        timestamp (int): Unix UTC timestamp of when the agent is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
        :param name:
    """

    inputs = [
        addresser.get_user_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_record_address(record_id)
    ]

    outputs = [addresser.get_record_address(record_id)]

    action = payload_pb2.CreateRecordAction(
        record_id=record_id,
        latitude=latitude,
        imageUrl=imageUrl,
        name=name,
        price=price,
        isForSale=isForSale,
        longitude=longitude)

    payload = payload_pb2.InfinityPayload(
        action=payload_pb2.InfinityPayload.CREATE_RECORD,
        create_record=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_transfer_record_transaction(transaction_signer,
                                     batch_signer,
                                     receiving_user,
                                     record_id,
                                     timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        receiving_user (str): Public key of the user receiving the record
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the record is transferred

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    sending_user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())
    receiving_user_address = addresser.get_user_address(receiving_user)
    record_address = addresser.get_record_address(record_id)

    inputs = [sending_user_address, receiving_user_address, record_address]

    outputs = [record_address]

    action = payload_pb2.TransferRecordAction(
        record_id=record_id,
        receiving_user=receiving_user)

    payload = payload_pb2.InfinityPayload(
        action=payload_pb2.InfinityPayload.TRANSFER_RECORD,
        transfer_record=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_update_record_location_transaction(transaction_signer,
                                            batch_signer,
                                            latitude,
                                            longitude,
                                            record_id,
                                            timestamp):
    """Make a UpdateRecordLocationAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        latitude (int): Updated latitude of the location
        longitude (int): Updated longitude of the location
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the record is updated

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())
    record_address = addresser.get_record_address(record_id)

    inputs = [user_address, record_address]

    outputs = [record_address]

    action = payload_pb2.UpdateRecordLocationAction(
        record_id=record_id,
        latitude=latitude,
        longitude=longitude)

    payload = payload_pb2.InfinityPayload(
        action=payload_pb2.InfinityPayload.UPDATE_RECORD_LOCATION,
        update_record_location=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_update_record_is_for_sale_transaction(transaction_signer,
                                               batch_signer,
                                               record_id,
                                               isForSale,
                                               timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        isForSale (bool): bool flag if record is for sale
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the record is updated

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    user_address = addresser.get_user_address(
        transaction_signer.get_public_key().as_hex())
    record_address = addresser.get_record_address(record_id)

    inputs = [user_address, record_address]

    outputs = [record_address]

    action = payload_pb2.UpdateRecordForSaleAction(
        record_id=record_id,
        isForSale=isForSale)

    payload = payload_pb2.InfinityPayload(
        action=payload_pb2.InfinityPayload.UPDATE_RECORD_FOR_SALE,
        update_record_for_sale=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def _make_batch(payload_bytes,
                inputs,
                outputs,
                transaction_signer,
                batch_signer):
    transaction_header = transaction_pb2.TransactionHeader(
        family_name=addresser.FAMILY_NAME,
        family_version=addresser.FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=transaction_signer.get_public_key().as_hex(),
        batcher_public_key=batch_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
    transaction_header_bytes = transaction_header.SerializeToString()

    transaction = transaction_pb2.Transaction(
        header=transaction_header_bytes,
        header_signature=transaction_signer.sign(transaction_header_bytes),
        payload=payload_bytes)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature])
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=[transaction])

    return batch
