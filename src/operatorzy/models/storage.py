class Storage:
    def __init__(self, id, capacity):
        self.name = id
        self.capacity = capacity
        self.current_level = 0

    def charge(self, amount):
        available_capacity = self.capacity - self.current_level
        charged = min(amount, available_capacity)
        self.current_level += charged
        return charged

    def discharge(self, amount):
        discharged = min(amount, self.current_level)
        self.current_level -= discharged
        return discharged