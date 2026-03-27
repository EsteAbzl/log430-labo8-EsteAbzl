"""
Kafka order event producer
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import config
from singleton import Singleton
from kafka import KafkaProducer

class OrderEventProducer(metaclass=Singleton):

  def __init__(self):
    """ Initialize KafkaProducer """
    self.producer = KafkaProducer(
      bootstrap_servers=config.KAFKA_HOST,
      value_serializer=lambda dict: json.dumps(dict).encode('utf-8')
    )

  def get_instance(self):
    return self.producer

# C'est pas du tout un singleton là, pour ça il faut que le constructeur soit privé et que self.producer soit une variable de classe. Ce qui n'est pas le cas vraissemblablement à part si je loupe quelque chose avec l'import de Singleton