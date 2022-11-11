import persistqueue

queue = persistqueue.SQLiteAckQueue('./car_queue')

queue.put("data")
