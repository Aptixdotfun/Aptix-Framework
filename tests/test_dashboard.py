import pytest
import os
from quart import Quart
from Aptixbot.dashboard.server import AptixBotDashboard
from Aptixbot.core.db.sqlite import SQLiteDatabase
from Aptixbot.core.core_lifecycle import AptixBotCoreLifecycle
from Aptixbot.core import LogBroker
from Aptixbot.core.star.star_handler import star_handlers_registry
from Aptixbot.core.star.star import star_registry


@pytest.fixture(scope="module")
def core_lifecycle_td():
    db = SQLiteDatabase("data/data_v3.db")
    log_broker = LogBroker()
    core_lifecycle_td = AptixBotCoreLifecycle(log_broker, db)
    return core_lifecycle_td

@pytest.fixture(scope="module")
def app(core_lifecycle_td):
    db = SQLiteDatabase("data/data_v3.db")
    server = AptixBotDashboard(core_lifecycle_td, db)
    return server.app

@pytest.fixture(scope="module")
def header():
    return {}

@pytest.mark.asyncio
async def test_init_core_lifecycle_td(core_lifecycle_td):
    await core_lifecycle_td.initialize()
    assert core_lifecycle_td is not None

@pytest.mark.asyncio
async def test_auth_login(app: Quart, core_lifecycle_td: AptixBotCoreLifecycle, header: dict):
    test_client = app.test_client()
    response = await test_client.post('/api/auth/login', json={
        "username": "wrong",
        "password": "password"
    })
    data = await response.get_json()
    assert data['status'] == 'error'
    
    response = await test_client.post('/api/auth/login', json={
        "username": core_lifecycle_td.Aptixbot_config['dashboard']['username'],
        "password": core_lifecycle_td.Aptixbot_config['dashboard']['password']
    })
    data = await response.get_json()
    assert data['status'] == 'ok' and 'token' in data['data']
    header['Authorization'] = f"Bearer {data['data']['token']}"
    
@pytest.mark.asyncio
async def test_get_stat(app: Quart, header: dict):
    test_client = app.test_client()
    response = await test_client.get('/api/stat/get')
    assert response.status_code == 401
    response = await test_client.get('/api/stat/get', headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok' and 'platform' in data['data']

@pytest.mark.asyncio
async def test_plugins(app: Quart, header: dict):
    test_client = app.test_client()
    # 已经安装的插件
    response = await test_client.get('/api/plugin/get', headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    
    # 插件市场
    response = await test_client.get('/api/plugin/market_list', headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    
    # 插件安装
    response = await test_client.post('/api/plugin/install', json={
        "url": "https://github.com/Aptix/Aptixbot_plugin_essential"
    }, headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    exists = False
    for md in star_registry:
        if md.name == "Aptixbot_plugin_essential":
            exists = True
            break
    assert exists is True, "插件 Aptixbot_plugin_essential 未成功载入"
    
    # 插件更新
    response = await test_client.post('/api/plugin/update', json={
        "name": "Aptixbot_plugin_essential"
    }, headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    
    # 插件卸载
    response = await test_client.post('/api/plugin/uninstall', json={
        "name": "Aptixbot_plugin_essential"
    }, headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    exists = False
    for md in star_registry:
        if md.name == "Aptixbot_plugin_essential":
            exists = True
            break
    assert exists is False, "插件 Aptixbot_plugin_essential 未成功卸载"
    exists = False
    for md in star_handlers_registry:
        if "Aptixbot_plugin_essential" in md.handler_module_path:
            exists = True
            break
    assert exists is False, "插件 Aptixbot_plugin_essential 未成功卸载"
    
@pytest.mark.asyncio
async def test_check_update(app: Quart, header: dict):
    test_client = app.test_client()
    response = await test_client.get('/api/update/check', headers=header)
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'success' 
    
@pytest.mark.asyncio
async def test_do_update(app: Quart, header: dict, core_lifecycle_td: AptixBotCoreLifecycle):
    global VERSION
    test_client = app.test_client()
    os.makedirs("data/Aptixbot_release", exist_ok=True)
    core_lifecycle_td.Aptixbot_updator.MAIN_PATH = "data/Aptixbot_release"
    VERSION = "114.514.1919810"
    response = await test_client.post('/api/update/do', headers=header, json={
        "version": "latest"
    })
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'error' # 已经是最新版本
    
    response = await test_client.post('/api/update/do', headers=header, json={
        "version": "v3.4.0",
        "reboot": False
    })
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'ok'
    assert os.path.exists("data/Aptixbot_release/Aptixbot")