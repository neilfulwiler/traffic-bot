import unittest
from backend_api import BackendApi

class TestBackend(unittest.TestCase):
    def test_one_event(self):
        experiment_id = 10
        user_ids = [1]

        backend = BackendApi('localhost', 8080)
        for user_id in user_ids:
            backend.log(experiment_id, user_id)
        results = backend.results(experiment_id)
        self.assertEqual(user_ids, results)

    def test_ten_thousand_events(self):
        experiment_id = 11
        user_ids = range(1000)
        backend = BackendApi('localhost', 8080)
        for user_id in user_ids:
            backend.log(experiment_id, user_id)
        results = backend.results(experiment_id)
        self.assertEqual(user_ids, results)

 #   def test_two_events(self):
        #experiment_id = 10
        #user_ids = [1, 2]

        #backend = BackendApi('localhost', 8080)
        #for user_id in user_ids:
            #backend.log(experiment_id, user_id)
        #results = backend.results(experiment_id)
 #       self.assertEqual(user_ids, results)



if __name__ == '__main__':
    unittest.main()
