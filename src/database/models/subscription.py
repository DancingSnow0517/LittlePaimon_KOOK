import datetime

from tortoise import Model, fields


class DailyNoteSub(Model):
    """
    原神实时便签提醒订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """用户id"""
    user_id: str = fields.CharField(max_length=15)
    """原神uid"""
    uid: str = fields.TextField()
    """上次提醒时间"""
    last_remind_time: datetime.datetime = fields.DatetimeField(null=True)

    class Meta:
        table = 'daily_note_sub'
        table_description = '原神实时便签提醒订阅'


class MihoyoBBSSub(Model):
    """
    米游社原神签到和米游币获取订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """用户id"""
    user_id: str = fields.CharField(max_length=15)
    """原神uid"""
    uid: str = fields.TextField()

    class Meta:
        table = 'mhy_bbs_sub'
        table_description = '米游社订阅'


class MihoyoBBSPostSub(Model):
    """
    米游社用户帖子订阅
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    mys_id: str = fields.CharField(max_length=255)
    """订阅的米游社用户id"""
    session_id: str = fields.CharField(max_length=255)
    """订阅者的qq号或群号"""
    session_type: str = fields.CharField(max_length=255, default='private')
    """订阅者的群号"""
    last_post_id: str = fields.CharField(max_length=255, null=True)
    """上次推送的帖子id"""

    class Meta:
        table = 'mhy_bbs_user_sub'
        table_description = '米游社用户帖子订阅'


class CloudGenshinSub(Model):
    """
    云原神
    """
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """用户id"""
    user_id: str = fields.CharField(max_length=15)
    """原神uid"""
    uid: str = fields.TextField()
    """uuid"""
    uuid: str = fields.CharField(max_length=255)
    """token"""
    token: str = fields.CharField(max_length=255)
    """自动签到状态"""
    auto_sign: bool = fields.BooleanField(default=False)

    class Meta:
        table = 'cloud_genshin_sub'
        table_description = '云原神订阅'
