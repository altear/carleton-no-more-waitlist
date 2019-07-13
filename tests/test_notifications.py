import pytest
import pandas as pd
from src.notifications import NotificationHandler
from src.utils import config_loader

def test_construct_message_no_updates():
    config = config_loader('config.yaml')
    nh = NotificationHandler(config)

    recipient = {
        'address': 'test@test.test',
        'notify_on': {
            'registration_success': False,
            'registration_failure': False
        }
    }

    data = {
        'registration_success': pd.DataFrame(),
        'registration_failure': pd.DataFrame()
    }
    assert nh.construct_message(recipient, data) is None