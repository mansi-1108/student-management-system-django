from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    roll_no = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

    def __str__(self):
        return self.name

    @property
    def grade(self):
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 75:
            return "A"
        elif self.marks >= 60:
            return "B"
        else:
            return "C"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    action = models.CharField(max_length=255)
    ip_address=models.GenericIPAddressField(null=True,blank=True)
    user_agent=models.TextField(blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"
    

