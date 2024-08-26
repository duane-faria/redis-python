class Store:
  data = {}

  @staticmethod
  def set_value(key, value):
    Store.data[key] = value

  @staticmethod
  def get_value(key):
    return Store.data[key]

  @staticmethod
  def delete_value(key):
    del Store.data[key]