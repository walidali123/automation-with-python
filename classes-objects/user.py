class User:
    def __init__(self, user_email, name, password, current_job_tittle):
        self.email = user_email
        self.name = name
        self.password = password
        self.current_job_tittle = current_job_tittle

    def change_password(self, new_password):
        self.password = new_password

    def change_job_tittle(self, new_job_tittle):
        self.current_job_tittle = new_job_tittle

    def get_user_info(self):
        print(f"User {self.name} currently works as a {self.current_job_tittle}.you can connect them at {self.email}")


"""app_user = User("nn@nn.com", "walid", "asd123", "DevOps Engineer")
app_user.get_user_info()
app_user.change_job_tittle("DevOps trianer")
app_user.get_user_info()"""


