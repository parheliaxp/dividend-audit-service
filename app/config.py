import os
from pathlib import Path
from omegaconf import OmegaConf
from app.logger import logger

class Config:
    """配置管理类"""

    def __init__(self):
        self.env = os.environ.get('ENV', 'dev')
        self.config = self._load_config()
        self.__dict__.update(self.config)
        self._initialize()

    def _load_config(self):
        """加载配置文件"""
        # 加载基础配置
        conf_path = Path(__file__).parent.parent / 'config/config.yaml'
        if not conf_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {conf_path}")
        default_conf = OmegaConf.load(str(conf_path))

        # 加载环境配置
        env_path = Path(__file__).parent.parent / f'config/env_{self.env}.yaml'
        if env_path.exists():
            env_conf = OmegaConf.load(str(env_path))
        else:
            env_conf = OmegaConf.create({})

        # 合并配置
        total_conf = OmegaConf.merge(default_conf, env_conf)
        return OmegaConf.to_container(total_conf)

    def _initialize(self):
        """初始化后处理"""
        pass

    def __getitem__(self, name):
        """支持字典式访问"""
        return self.config[name]

    def show(self):
        """显示配置"""
        return OmegaConf.to_yaml(self.config)

cfg = Config()
logger.info("当前 ENV: {}".format(cfg.env))
