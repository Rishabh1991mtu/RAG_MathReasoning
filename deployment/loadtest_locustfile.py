from locust import HttpUser,task, between 

class RAGUser(HttpUser):
    
    wait_time = between(1, 2)
    
    @task
    def query_rag(self):
        self.client.post("/api/math-query", json={
            "prompt": "What is the integral of x^2?",
            "top_k_param": 3
        })
    
if __name__ == "__main__":
    import os
    os.system("locust -f deployment/loadtest_locustfile.py --host=http://127.0.0.1:8000")
    
