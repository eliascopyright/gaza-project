from pathlib import Path
import yaml
from hdx.api.configuration import Configuration
import hdx.api.configuration
from logging.handlers import RotatingFileHandler
import logging


BASE_DIR = Path(__file__).parent.parent.resolve()

class Utilis:
 def load_cfg():
  config_path = BASE_DIR/'config.yaml'
  with open(config_path, "r") as f:
   return yaml.safe_load(f)
 
 def setup_logging(logger_name: str, log_path: str):
  
  logger = logging.getLogger(name = logger_name)
  if logger.hasHandlers():
   logger.handlers.clear()
  logger.setLevel(logging.DEBUG)
  
  formatter_file = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s")
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)
  formatter_console = logging.Formatter('%(levelname)s | %(filename)s | %(message)s')
  console_handler.setFormatter(formatter_console)
  
  logs_path = Path(Utilis.load_cfg()['paths']['logs'])
  logs_path.mkdir(exist_ok=True, parents = True)
  
  file_handler = RotatingFileHandler(logs_path/log_path, maxBytes = 5*1024*1024, backupCount = 3, encoding = 'utf-8')
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter_file)
  
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)
  
  logger.propagate = False
  
  return logger
  
 def loadConfiguration():
    try:
        Configuration.read()
    except hdx.api.configuration.ConfigurationError:
        Configuration.create(hdx_site="prod", user_agent="gaza-project", hdx_read_only=True)