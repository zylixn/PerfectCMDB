from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,Group
)
try:
    from Crypto.Cipher import AES
except ModuleNotFoundError:
    pass
import base64


def get_AES(password, encode=1):
    # 密码加密

    KEY = '1234567890123456'
    BLOCK_SIZE = 16  # AES.block_size
    PADDING = chr(20)  # 'ý' #未满16*n时，补齐字符chr(253)

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    cipher = AES.new(KEY)
    if encode:
        # 密码加密，用于内部保存
        # try:
        #     decoded = DecodeAES(cipher, password)
        # return  password #未修改密码直接提交，原字符已为密文，无需再次加密
        # except:
        #     pass
        return EncodeAES(cipher, password)  # 修改了密码，重新加密为密文
    else:
        # 密码解密，用于外部提取
        try:
            return DecodeAES(cipher, password)
        except:
            print('Error: AES密码解密失败！！')
            return ''

class Menu(models.Model):
    '''动态菜单'''
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('self',verbose_name=u'父级菜单',null=True,blank=True,default='0',\
                               help_text=u'如果添加的是子菜单，请选择父菜单',on_delete=models.CASCADE)
    show = models.BooleanField(verbose_name=u'是否显示',default=False,help_text=u'菜单是否显示，默认添加不显示')
    priority = models.IntegerField(verbose_name=u'显示优先级',null=True,blank=True,default=-1,\
                                   help_text=u'菜单的显示顺序，优先级越大显示越靠前')
    permission_id = models.IntegerField(verbose_name=u'权限编号',help_text=u'给菜单设置一个编号，用于权限控制',\
                                        error_messages={'field-permission_id': u'只能输入数字'},default=0)
    #绝对url和动态url
    url_type_choices = ((0,'absolute'),(1,'dynamic'))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name = models.CharField(max_length=128)
    url_alias = models.CharField(max_length=64,null=True,blank=True)
    class_name = models.CharField(max_length=64,null=True,blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name','url_name')
        ordering = ["-priority", "id"]

class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField("Menu",blank=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = "role"

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(max_length=64)
    role = models.ManyToManyField('Role')
    token = models.CharField(u'token', max_length=128,default=None,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password',]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        #db_table = "userprofile"
        pass

class ServerInfor(models.Model):
    name = models.CharField(max_length=40, verbose_name=_('Server name'), blank=False, unique=True)
    hostname = models.CharField(max_length=40, verbose_name=_('Host name'), blank=True)
    ip = models.GenericIPAddressField(protocol='ipv4', verbose_name=_('ip'), blank=False)
    createdatetime = models.DateTimeField(auto_now_add=True, verbose_name=_('Create time'))
    updatedatetime = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('Update time'))
    credential = models.ForeignKey('Credential',on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "serverinfor"
        unique_together = (("ip", "credential"),)
        permissions = (
            ("can_add_serverinfo", _("Can add server")),
            ("can_change_serverinfo", _("Can change server info")),
            ("can_delete_serverinfo", _("Can delete server info")),
            ("can_connect_serverinfo", _("Can connect to server")),
            ("can_kill_serverinfo", _("Can kill online user")),
            ("can_monitor_serverinfo", _("Can monitor user action")),
            ("can_view_serverinfo", _("Can view server info")),
            ("can_filemanage_serverinfo", _("Can manage file")),
        )

class ServerGroup(models.Model):
    name = models.CharField(max_length=40, verbose_name=_('Server group name'), blank=False, unique=True)
    servers = models.ManyToManyField(ServerInfor, related_name='servers', verbose_name=_('Servers'))
    createdatetime = models.DateTimeField(auto_now_add=True, verbose_name=_('Create time'))
    updatedatetime = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('Update time'))

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "servergroup"
        permissions = (
            ("can_add_servergroup", _("Can add group")),
            ("can_change_servergroup", _("Can change group info")),
            ("can_delete_servergroup", _("Can delete group info")),
            ("can_view_servergroup", _("Can view group info")),
        )

class Credential(models.Model):
    protocol_choices = (
        ('ssh-password', _('ssh-password')),
        ('ssh-key', _('ssh-key')),
        ('ssh-key-with-password', _('ssh-key-with-password')),
        ('vnc', _('vnc')),
        ('rdp', _('rdp')),
        ('telnet', _('telnet'))
    )
    security_choices = (
        ('rdp', _('Standard RDP encryption')),
        ('nla', _('Network Level Authentication')),
        ('tls', _('TLS encryption')),
        ('any', _('Allow the server to choose the type of security')),
    )
    name = models.CharField(max_length=40, verbose_name=_('Credential name'), blank=False, unique=True)
    username = models.CharField(max_length=40, verbose_name=_('Auth user name'), blank=False)
    port = models.PositiveIntegerField(default=22, blank=False, verbose_name=_('Port'))
    method = models.CharField(max_length=40, choices=(('password', _('password')), ('key', _('key'))), blank=False,
                              default='password', verbose_name=_('Method'))
    key = models.TextField(blank=True, verbose_name=_('Key'))
    password = models.CharField(max_length=40, blank=True, verbose_name=_('Password'))
    proxy = models.BooleanField(default=False, verbose_name=_('Proxy'))
    proxyserverip = models.GenericIPAddressField(protocol='ipv4', null=True, blank=True, verbose_name=_('Proxy ip'))
    proxyport = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Proxy port'))
    proxypassword = models.CharField(max_length=40, verbose_name=_('Proxy password'), blank=True)
    protocol = models.CharField(max_length=40, default='ssh-password', choices=protocol_choices,
                                verbose_name=_('Protocol'))
    width = models.PositiveIntegerField(verbose_name=_('width'), default=1024)
    height = models.PositiveIntegerField(verbose_name=_('height'), default=768)
    dpi = models.PositiveIntegerField(verbose_name=_('dpi'), default=96)
    security = models.CharField(max_length=40, default='any', choices=security_choices, verbose_name=_('Security'))

    def __str__(self):
        return self.name

    def clean(self):
        if self.protocol == 'ssh-password' or self.protocol == 'ssh-key':
            if self.method == 'password' and len(self.password) == 0:
                raise ValidationError(_('If you choose password auth method,You must set password!'))
            if self.method == 'password' and len(self.key) > 0:
                raise ValidationError(_('If you choose password auth method,You must make key field for blank!'))
            if self.method == 'key' and len(self.key) == 0:
                raise ValidationError(_('If you choose key auth method,You must fill in key field!'))
            if self.method == 'key' and len(self.password) > 0:
                raise ValidationError(_('If you choose key auth method,You must make password field for blank!'))
            if self.proxy:
                if self.proxyserverip is None or self.proxyport is None:
                    raise ValidationError(
                        _('If you choose auth proxy,You must fill in proxyserverip and proxyport field !'))

    class Meta:
        #db_table = "credential"
        permissions = (
            ("can_add_credential", _("Can add credential")),
            ("can_change_credential", _("Can change credential info")),
            ("can_delete_credential", _("Can delete credential info")),
            ("can_view_credential", _("Can view credential info")),
        )
    
    # def save(self, *args, **kwargs):
    #     if self.password:
    #         password_aes = get_AES(password=self.password)
    #         self.password = password_aes
    #     elif self.id:
    #         del self.password # 防止不修改密码时，提交的空密码覆盖
    #     super(Credential, self).save(*args,**kwargs)

class AssetGroup(models.Model):
    name = models.CharField("组名/区域",max_length=30,unique=True)
    desc = models.CharField("描述",max_length=100,null=True,blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = '主机分组'

    def __str__(self):
        return self.name

    class Meta:
        #db_table = "assetgroup"
        pass

class Asset(models.Model):
    asset_type_choices = (
        ('server', u'服务器'),
        ('networkdevice', u'网络设备'),
        ('storagedevice', u'存储设备'),
        ('securitydevice', u'安全设备'),
        ('securitydevice', u'机房设备'),
        ('software', u'软件资产'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, default='server')
    name = models.CharField(max_length=64, unique=True)
    sn = models.CharField(u'资产SN号', max_length=128, unique=True)
    manufactory = models.ForeignKey('Manufactory', verbose_name=u'制造商', null=True, blank=True,on_delete=models.CASCADE)
    management_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    contract = models.ForeignKey('Contract', verbose_name=u'合同', null=True, blank=True,on_delete=models.CASCADE)
    trade_date = models.DateField(u'购买时间', null=True, blank=True)
    expire_date = models.DateField(u'过保修期', null=True, blank=True)
    price = models.FloatField(u'价格', null=True, blank=True)
    business_unit = models.ForeignKey('BusinessUnit', verbose_name=u'所属业务线', null=True, blank=True,on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    #admin = models.ForeignKey('UserProfile', verbose_name=u'资产管理员', null=True, blank=True,on_delete=models.CASCADE)
    idc = models.ForeignKey('IDC', verbose_name=u'IDC机房', null=True, blank=True,on_delete=models.CASCADE)
    group = models.ForeignKey(AssetGroup, verbose_name=u"组/安全区域", default=1, on_delete=models.SET_NULL, null=True,
                              blank=True)
    usergroup = models.ManyToManyField(Group,verbose_name='网站用户组',blank=True,help_text='网站哪些用户组可以对主机进行操作')
    user = models.ManyToManyField(UserProfile,verbose_name='网站用户权限', blank=True,
                                  # through='Host_User',  # 行级别的权限控制，人工录入时麻烦，比较困难实现快速批量设置主机清单
                                  help_text='网站哪些用户能对当前主机进行操作，超级用户直接有操作权限')
    status_choices = ((0, '在线'),
                      (1, '已下线'),
                      (2, '未知'),
                      (3, '故障'),
                      (4, '备用'),
                      )
    status = models.SmallIntegerField(choices=status_choices, default=0)
    credential = models.ForeignKey('Credential', on_delete=models.CASCADE)
    memo = models.TextField(u'备注', null=True, blank=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        permissions = (
            # 实现表级别的权限控制
            ("deploy_asset", "Can deploy asset"),  # APP部署
            ("webssh_asset", "Can webssh asset"),  # 终端登陆
            ("grep_asset", "Can grep asset"),  # 执行日志搜索
            ("run_sh_asset", "Can run_sh asset"),  # 执行常用命令
            ("run_cmd_asset", "Can run_cmd asset"),  # 执行自定义命令
            ("other_do_asset", "Can other_do asset"),  # 执行其它操作，如ES节点索引
        )

        #db_table = "asset"

    def __str__(self):
        return '%s#%s'%(self.name,self.management_ip)

    def chk_user_perm(self,user,perm):
        if user.is_admin:
            return 1
        elif not user.has_perm('cmdb.%s_asset'%perm):
            return 0
        elif user in self.user.all() or self.admin == user:
            return 1 # 主机有设置设置用户为网站操作用户/负责人

        usergroups = self.usergroup.all()
        for usergroup in usergroups:
            if user in usergroup.user_set.all():
                return 1
        return 0

    def get_ssh_user(self):
        # 获取某台主机SSH用户/密码
        credential = self.credential
        if not credential:
            ssh_users = Credential.objects.all()
            if ssh_users:
                ssh_user = ssh_users[0]
            else:
                print("为找到对应的用户")
                return
        username = ssh_user.username
        password = get_AES(password=ssh_user.password,encode=0)
        return username,password

    @staticmethod
    def get_user_asset(user):
        # 获取用户有操作权限的所有主机
        assets = Asset.objects.all()
        if user.is_admin:
            return assets

        assets1 = assets.filter(user=user) # 已设置用户为操作用户
        return assets1

class Server(models.Model):
    """服务器设备"""
    asset = models.OneToOneField('Asset',on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, 'PC服务器'),
        (1, '刀片机'),
        (2, '小型机'),
    )
    created_by_choices = (
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="服务器类型", default=0)
    created_by = models.CharField(choices=created_by_choices, max_length=32,
                                  default='auto')  # auto: auto created,   manual:created manually
    hosted_on = models.ForeignKey('self', related_name='hosted_on_server', blank=True, null=True,on_delete=models.CASCADE)  # for vitural server
    # sn = models.CharField(u'SN号',max_length=128)
    # management_ip = models.CharField(u'管理IP',max_length=64,blank=True,null=True)
    # manufactory = models.ForeignKey(verbose_name=u'制造商',max_length=128,null=True, blank=True)
    model = models.CharField(verbose_name=u'型号', max_length=128, null=True, blank=True)
    # 若有多个CPU，型号应该都是一致的，故没做ForeignKey

    # nic = models.ManyToManyField('NIC', verbose_name=u'网卡列表')
    # disk
    raid_type = models.CharField(u'raid类型', max_length=512, blank=True, null=True)
    # physical_disk_driver = models.ManyToManyField('Disk', verbose_name=u'硬盘',blank=True,null=True)
    # raid_adaptor = models.ManyToManyField('RaidAdaptor', verbose_name=u'Raid卡',blank=True,null=True)
    # memory
    # ram_capacity = models.IntegerField(u'内存总大小GB',blank=True)
    # ram = models.ManyToManyField('Memory', verbose_name=u'内存配置',blank=True,null=True)

    os_type = models.CharField(u'操作系统类型', max_length=64, blank=True, null=True)
    os_distribution = models.CharField(u'发行版本', max_length=64, blank=True, null=True)
    os_release = models.CharField(u'操作系统版本', max_length=64, blank=True, null=True)

    class Meta:
        #db_table = "server"
        pass

    def __str__(self):
        return '%s sn:%s' % (self.asset.name, self.asset.sn)

class SecurityDevice(models.Model):
    """安全设备"""
    asset = models.OneToOneField('Asset',on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, '防火墙'),
        (1, '入侵检测设备'),
        (2, '互联网网关'),
        (4, '运维审计系统'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="服务器类型", default=0)

    def __str__(self):
        return self.asset.id

    class Meta:
        db_table = "securitydevice"

class NetworkDevice(models.Model):
    """网络设备"""

    asset = models.OneToOneField('Asset',on_delete=models.CASCADE)
    sub_assset_type_choices = (
        (0, '路由器'),
        (1, '交换机'),
        (2, '负载均衡'),
        (4, 'VPN设备'),
    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="服务器类型", default=0)

    vlan_ip = models.GenericIPAddressField(u'VlanIP', blank=True, null=True)
    intranet_ip = models.GenericIPAddressField(u'内网IP', blank=True, null=True)
    # sn = models.CharField(u'SN号',max_length=128,unique=True)
    # manufactory = models.CharField(verbose_name=u'制造商',max_length=128,null=True, blank=True)
    model = models.CharField(u'型号', max_length=128, null=True, blank=True)
    firmware = models.ForeignKey('Software', blank=True, null=True,on_delete=models.CASCADE)
    port_num = models.SmallIntegerField(u'端口个数', null=True, blank=True)
    device_detail = models.TextField(u'设置详细配置', null=True, blank=True)

    class Meta:
        db_table = "networkdevice"

class Software(models.Model):
    '''
    only save software which company purchased
    '''
    sub_assset_type_choices = (
        (0, 'OS'),
        (1, '办公\开发软件'),
        (2, '业务软件'),

    )
    sub_asset_type = models.SmallIntegerField(choices=sub_assset_type_choices, verbose_name="服务器类型", default=0)
    license_num = models.IntegerField(verbose_name="授权数")
    # os_distribution_choices = (('windows','Windows'),
    #                            ('centos','CentOS'),
    #                            ('ubuntu', 'Ubuntu'))
    # type = models.CharField(u'系统类型', choices=os_types_choice, max_length=64,help_text=u'eg. GNU/Linux',default=1)
    # distribution = models.CharField(u'发型版本', choices=os_distribution_choices,max_length=32,default='windows')
    version = models.CharField(u'软件/系统版本', max_length=64, help_text=u'eg. CentOS release 6.5 (Final)', unique=True)

    # language_choices = (('cn',u'中文'),
    #                     ('en',u'英文'))
    # language = models.CharField(u'系统语言',choices = language_choices, default='cn',max_length=32)
    # #version = models.CharField(u'版本号', max_length=64,help_text=u'2.6.32-431.3.1.el6.x86_64' )

    def __str__(self):
        return self.version

    class Meta:
        db_table = "software"

class CPU(models.Model):
    """CPU组件"""

    asset = models.OneToOneField('Asset',on_delete=models.CASCADE)
    cpu_model = models.CharField(u'CPU型号', max_length=128, blank=True)
    cpu_count = models.SmallIntegerField(u'物理cpu个数')
    cpu_core_count = models.SmallIntegerField(u'cpu核数')
    memo = models.TextField(u'备注', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        pass

    def __str__(self):
        return self.cpu_model

class RAM(models.Model):
    """内存组件"""

    asset = models.ForeignKey('Asset',on_delete=models.CASCADE)
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    model = models.CharField(u'内存型号', max_length=128)
    slot = models.CharField(u'插槽', max_length=64)
    capacity = models.IntegerField(u'内存大小(MB)')
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '%s:%s:%s' % (self.asset_id, self.slot, self.capacity)

    class Meta:
        unique_together = ("asset", "slot")

    auto_create_fields = ['sn', 'slot', 'model', 'capacity']

class Disk(models.Model):
    """硬盘组件"""

    asset = models.ForeignKey('Asset',on_delete=models.CASCADE)
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    slot = models.CharField(u'插槽位', max_length=64)
    # manufactory = models.CharField(u'制造商', max_length=64,blank=True,null=True)
    model = models.CharField(u'磁盘型号', max_length=128, blank=True, null=True)
    capacity = models.FloatField(u'磁盘容量GB')
    disk_iface_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
    )

    iface_type = models.CharField(u'接口类型', max_length=64, choices=disk_iface_choice, default='SAS')
    memo = models.TextField(u'备注', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    auto_create_fields = ['sn', 'slot', 'manufactory', 'model', 'capacity', 'iface_type']

    class Meta:
        unique_together = ("asset", "slot")

    def __str__(self):
        return '%s:slot:%s capacity:%s' % (self.asset_id, self.slot, self.capacity)

class NIC(models.Model):
    """网卡组件"""

    asset = models.ForeignKey('Asset',on_delete=models.CASCADE)
    name = models.CharField(u'网卡名', max_length=64, blank=True, null=True)
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    model = models.CharField(u'网卡型号', max_length=128, blank=True, null=True)
    macaddress = models.CharField(u'MAC', max_length=64, unique=True)
    ipaddress = models.GenericIPAddressField(u'IP', blank=True, null=True)
    netmask = models.CharField(max_length=64, blank=True, null=True)
    bonding = models.CharField(max_length=64, blank=True, null=True)
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '%s:%s' % (self.asset_id, self.macaddress)

    class Meta:
        # unique_together = ("asset_id", "slot")
        unique_together = ("asset", "macaddress")

    auto_create_fields = ['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask', 'bonding']

class RaidAdaptor(models.Model):
    """Raid卡"""

    asset = models.ForeignKey('Asset',on_delete=models.CASCADE)
    sn = models.CharField(u'SN号', max_length=128, blank=True, null=True)
    slot = models.CharField(u'插口', max_length=64)
    model = models.CharField(u'型号', max_length=64, blank=True, null=True)
    memo = models.TextField(u'备注', blank=True, null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("asset", "slot")

class Manufactory(models.Model):
    """厂商"""

    manufactory = models.CharField(u'厂商名称', max_length=64, unique=True)
    support_num = models.CharField(u'支持电话', max_length=30, blank=True)
    memo = models.CharField(u'备注', max_length=128, blank=True)

    def __str__(self):
        return self.manufactory

    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = "厂商"

class BusinessUnit(models.Model):
    """业务线"""

    parent_unit = models.ForeignKey('self', related_name='parent_level', blank=True, null=True,on_delete=models.CASCADE)
    name = models.CharField(u'业务线', max_length=64, unique=True)

    # contact = models.ForeignKey('UserProfile',default=None)
    memo = models.CharField(u'备注', max_length=64, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = "业务线"

class Contract(models.Model):
    """合同"""

    sn = models.CharField(u'合同号', max_length=128, unique=True)
    name = models.CharField(u'合同名称', max_length=64)
    memo = models.TextField(u'备注', blank=True, null=True)
    price = models.IntegerField(u'合同金额')
    detail = models.TextField(u'合同详细', blank=True, null=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    license_num = models.IntegerField(u'license数量', blank=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = '合同'
        verbose_name_plural = "合同"

    def __str__(self):
        return self.name

class IDC(models.Model):
    """机房"""

    name = models.CharField(u'机房名称', max_length=64, unique=True)
    memo = models.CharField(u'备注', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"

class Tag(models.Model):
    """资产标签"""

    name = models.CharField('Tag name', max_length=32, unique=True)
    creator = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class EventLog(models.Model):
    """事件"""

    name = models.CharField(u'事件名称', max_length=100)
    event_type_choices = (
        (1, u'硬件变更'),
        (2, u'新增配件'),
        (3, u'设备下线'),
        (4, u'设备上线'),
        (5, u'定期维护'),
        (6, u'业务上线\更新\变更'),
        (7, u'其它'),
    )
    event_type = models.SmallIntegerField(u'事件类型', choices=event_type_choices)
    asset = models.ForeignKey('Asset',on_delete=models.CASCADE)
    component = models.CharField('事件子项', max_length=255, blank=True, null=True)
    detail = models.TextField(u'事件详情')
    date = models.DateTimeField(u'事件时间', auto_now_add=True)
    user = models.ForeignKey('UserProfile', verbose_name=u'事件源',on_delete=models.CASCADE)
    memo = models.TextField(u'备注', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '事件纪录'
        verbose_name_plural = "事件纪录"

    def colored_event_type(self):
        if self.event_type == 1:
            cell_html = '<span style="background: orange;">%s</span>'
        elif self.event_type == 2:
            cell_html = '<span style="background: yellowgreen;">%s</span>'
        else:
            cell_html = '<span >%s</span>'
        return cell_html % self.get_event_type_display()

    colored_event_type.allow_tags = True
    colored_event_type.short_description = u'事件类型'

class NewAssetApprovalZone(models.Model):
    """新资产待审批区"""

    sn = models.CharField(u'资产SN号', max_length=128, unique=True)
    asset_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('router', u'路由器'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('NLB', u'NetScaler'),
        ('wireless', u'无线AP'),
        ('software', u'软件资产'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices, max_length=64, blank=True, null=True)
    manufactory = models.CharField(max_length=64, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    ram_size = models.IntegerField(blank=True, null=True)
    cpu_model = models.CharField(max_length=128, blank=True, null=True)
    cpu_count = models.IntegerField(blank=True, null=True)
    cpu_core_count = models.IntegerField(blank=True, null=True)
    os_distribution = models.CharField(max_length=64, blank=True, null=True)
    os_type = models.CharField(max_length=64, blank=True, null=True)
    os_release = models.CharField(max_length=64, blank=True, null=True)
    data = models.TextField(u'资产数据')
    date = models.DateTimeField(u'汇报日期', auto_now_add=True)
    approved = models.BooleanField(u'已批准', default=False)
    approved_by = models.ForeignKey('UserProfile', verbose_name=u'批准人', blank=True, null=True,on_delete=models.CASCADE)
    approved_date = models.DateTimeField(u'批准日期', blank=True, null=True)

    def __str__(self):
        return self.sn

    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = "新上线待批准资产"