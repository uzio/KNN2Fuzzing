# coding:utf-8


class Case:
    class Meta:
        database = 'fuzz'
        collection = 'case'
        indexes = ['title']


class Job:
    """
    title
    percentage
    job_type
    time
    creator
    description
    status
    cases
    """
    class Meta:
        database = 'fuzz'
        collection = 'job'
        indexes = ['title']

