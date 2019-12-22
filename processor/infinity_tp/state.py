from infinity_addressing import addresser

from infinity_protobuf import user_pb2
from infinity_protobuf import record_pb2





def set_role(role):
    if role == "Admin":
        return user_pb2.User.RoleType.Admin
    elif role == "Creator":
        return user_pb2.User.RoleType.Creator
    elif role == "User":
        return user_pb2.User.RoleType.User
    elif role == "Querier":
        return user_pb2.User.RoleType.Querier
    else:
        return user_pb2.User.RoleType.Admin
        # raise ValueError('Role not supported')


class InfinityState(object):
    def __init__(self, context, timeout=2):
        self._context = context
        self._timeout = timeout

    def get_user(self, public_key):
        """Gets the user associated with the public_key

        Args:
            public_key (str): The public key of the user

        Returns:
            user_pb2.User: User with the provided public_key
        """
        address = addresser.get_user_address(public_key)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = user_pb2.UserContainer()
            container.ParseFromString(state_entries[0].data)
            for user in container.entries:
                if user.public_key == public_key:
                    return user

        return None

    def set_user(self, public_key, name, timestamp, role):
        """Creates a new user in state

        Args:
            public_key (str): The public key of the user
            name (str): The human-readable name of the user
            role(str): The role of user, accepted values [Admin, Creator, User, Querier]
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.get_user_address(public_key)

        user = user_pb2.User(
            public_key=public_key, name=name, timestamp=timestamp, role=role)
        container = user_pb2.UserContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([user])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_record(self, record_id):
        """Gets the record associated with the record_id

        Args:
            record_id (str): The id of the record

        Returns:
            record_pb2.Record: Record with the provided record_id
        """
        address = addresser.get_record_address(record_id)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = record_pb2.RecordContainer()
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    return record

        return None

    def set_record(self,
                   public_key,
                   latitude,
                   longitude,
                   record_id,
                   name,
                   imageUrl,
                   price,
                   isForSale,
                   timestamp):
        """Creates a new record in state

        Args:
            public_key (str): The public key of the user creating the record
            latitude (int): Initial latitude of the record
            longitude (int): Initial latitude of the record
            record_id (str): Unique ID of the record
            name (str): Name of the record
            imageUrl(str, Optional): Image of the record
            price (str): Price of record if record has price
            isForSale(bool): Flag if product is for sale
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.get_record_address(record_id)
        owner = record_pb2.Record.Owner(
            user_id=public_key,
            timestamp=timestamp)
        creator = record_pb2.Record.Creator(
            user_id=public_key,
            timestamp=timestamp)
        location = record_pb2.Record.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        record = record_pb2.Record(
            record_id=record_id,
            name=name,
            imageUrl=imageUrl,
            price=price,
            isForSale= isForSale,
            owners=[owner],
            creator=creator,
            locations=[location],
            created_timestamp=timestamp,
            )
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([record])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def transfer_record(self, receiving_user, record_id, timestamp):
        owner = record_pb2.Record.Owner(
            user_id=receiving_user,
            timestamp=timestamp)
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.owners.extend([owner])
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_record_location(self, latitude, longitude, record_id, timestamp):
        location = record_pb2.Record.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.locations.extend([location])
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)


    def update_record_is_for_sale(self, record_id, isForSale, timestamp):
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.isForSale = isForSale
                    record.updated_timestamp = timestamp
            data = container.SerializeToString()
            updated_state = {}
            updated_state[address] = data
            self._context.set_state(updated_state, timeout=self._timeout)

    def update_record_is_stolen(self, record_id, is_stolen, timestamp):
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.is_stolen = is_stolen
                    record.updated_timestamp = timestamp
            data = container.SerializeToString()
            updated_state = {}
            updated_state[address] = data
            self._context.set_state(updated_state, timeout=self._timeout)