<script setup>
import ExtensionCard from '@/components/shared/ExtensionCard.vue';
import WaitingForRestart from '@/components/shared/WaitingForRestart.vue';
import AptixBotConfig from '@/components/shared/AptixBotConfig.vue';
import ConsoleDisplayer from '@/components/shared/ConsoleDisplayer.vue';
import axios from 'axios';
import { max } from 'date-fns';

</script>

<template>
  <v-row>
    <v-alert style="margin: 16px" text="1. 如果因为网络问题安装失败，可以自行前往仓库下载压缩包，然后从本地上传。2. 如需插件帮助请点击 `仓库` 查看 README" title="💡提示"
      type="info" variant="tonal">
    </v-alert>
    <v-col cols="12" md="12">
      <div style="background-color: white; width: 100%; padding: 16px; border-radius: 10px;">
        <div style="display: flex; align-items: center;">
          <h3>🧩 已安装的插件</h3>

          <v-dialog max-width="500px">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" v-if="extension_data.message" icon size="small" color="error"
                style="margin-left: auto;" variant="plain">
                <v-icon>mdi-alert-circle</v-icon>
              </v-btn>
            </template>

            <template v-slot:default="{ isActive }">
              <v-card>
                <v-card-title class="headline">错误信息</v-card-title>
                <v-card-text>{{ extension_data.message }}
                  <br>
                  <small>详情请检查控制台</small>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" text @click="isActive.value = false">关闭</v-btn>
                </v-card-actions>
              </v-card>
            </template>

          </v-dialog>
        </div>
      </div>
    </v-col>
    <v-col cols="12" md="6" lg="3" v-for="extension in extension_data.data">
      <ExtensionCard :key="extension.name" :title="extension.name" :link="extension.repo" :logo="extension?.logo"
        style="margin-bottom: 4px;">
        <div style="min-height: 135px; max-height: 135px; overflow: none;">
          <span style="font-weight: bold;">By @{{ extension.author }}</span>
          <span> | 插件有 {{ extension.handlers.length }} 个行为</span>
          <p style="margin-top: 8px;">{{ extension.desc }}</p>
          <a style="font-size: 12px; cursor: pointer; text-decoration: underline; color: #555;"
            @click="reloadPlugin(extension.name)">重载插件</a>
        </div>
        <div class="d-flex align-center gap-2 " style="overflow-x: auto;">
          <v-btn v-if="!extension.reserved" class="text-none mr-2" size="small" text="Read" variant="flat" border
            @click="openExtensionConfig(extension.name)">配置</v-btn>
          <v-btn v-if="!extension.reserved" class="text-none mr-2" size="small" text="Read" variant="flat" border
            @click="updateExtension(extension.name)">更新</v-btn>
          <v-btn v-if="!extension.reserved" class="text-none mr-2" size="small" text="Read" variant="flat" border
            @click="uninstallExtension(extension.name)">卸载</v-btn>
          <!-- <span v-else>保留插件</span> -->
          <v-btn class="text-none mr-2" size="small" text="Read" variant="flat" border v-if="extension.activated"
            @click="pluginOff(extension)">禁用</v-btn>
          <v-btn class="text-none mr-2" size="small" text="Read" variant="flat" border v-else
            @click="pluginOn(extension)">启用</v-btn>

          <v-btn class="text-none mr-2" size="small" text="Read" variant="flat" border
            @click="showPluginInfo(extension)">行为</v-btn>
        </div>
      </ExtensionCard>
    </v-col>
    <v-col cols="12" md="12">
      <div style="background-color: white; width: 100%; padding: 16px; border-radius: 10px;">
        <div style="display: flex; align-items: center;">
          <h3>🧩 插件市场</h3>
          <small style="margin-left: 16px;">如无法显示，请打开 <a
              href="https://Aptix.github.io/AptixBot_Plugins_Collection/plugins.json">链接</a> 复制想安装插件对应的 `repo`
            链接然后点击右下角 + 号安装，或打开链接下载压缩包安装。</small>
          <v-btn icon @click="isListView = !isListView" size="small" style="margin-left: auto;" variant="plain">
            <v-icon>{{ isListView ? 'mdi-view-grid' : 'mdi-view-list' }}</v-icon>
          </v-btn>
        </div>
      </div>
    </v-col>

    <v-col cols="12" md="12" v-if="announcement">
      <v-banner color="success" lines="one" :text="announcement" :stacked="false">
      </v-banner>
    </v-col>

    <template v-if="isListView">
      <v-col cols="12" md="12">
        <v-data-table :headers="pluginMarketHeaders" :items="pluginMarketData" item-key="name">
          <template v-slot:item.actions="{ item }">
            <v-btn v-if="!item.installed" class="text-none mr-2" size="small" text="Read" variant="flat" border
              @click="extension_url = item.repo; newExtension()">安装</v-btn>
            <v-btn v-else class="text-none mr-2" size="small" text="Read" variant="flat" border disabled>已安装</v-btn>
          </template>
        </v-data-table>
      </v-col>
    </template>
    <template v-else>
      <v-col cols="12" md="6" lg="3" v-for="plugin in pluginMarketData">
        <ExtensionCard :key="plugin.name" :title="plugin.name" :link="plugin.repo" style="margin-bottom: 4px;">
          <div style="min-height: 130px; max-height: 130px; overflow: hidden;">
            <p style="font-weight: bold;">By @{{ plugin.author }}</p>
            {{ plugin.desc }}
          </div>
          <div class="d-flex align-center gap-2">
            <v-btn v-if="!plugin.installed" class="text-none mr-2" size="small" text="Read" variant="flat" border
              @click="extension_url = plugin.repo; newExtension()">安装</v-btn>
            <v-btn v-else class="text-none mr-2" size="small" text="Read" variant="flat" border disabled>已安装</v-btn>
          </div>
        </ExtensionCard>
      </v-col>
    </template>

    <v-col style="margin-bottom: 16px;" cols="12" md="12">
      <small><a href="https://Aptixbot.app/dev/plugin.html">插件开发文档</a></small> |
      <small> <a href="https://github.com/Aptix/AptixBot_Plugins_Collection">提交插件仓库</a></small>
    </v-col>

  </v-row>

  <v-dialog v-model="configDialog" width="1000">
    <template v-slot:activator="{ props }">
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">插件配置</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <AptixBotConfig v-if="extension_config.metadata" :metadata="extension_config.metadata"
            :iterable="extension_config.config" :metadataKey=curr_namespace></AptixBotConfig>
          <p v-else>这个插件没有配置</p>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="updateConfig">
          保存并关闭
        </v-btn>
        <v-btn color="blue-darken-1" variant="text" @click="configDialog = false">
          关闭
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="dialog" width="700">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" icon="mdi-plus" size="x-large" style="position: fixed; right: 52px; bottom: 52px;"
        color="darkprimary">
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">安装插件</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <h3>从 GitHub 上在线下载</h3>
            <v-col cols="12">
              <small>请输入合法的 GitHub 仓库链接，当前仅支持 GitHub。如：https://github.com/Aptix/Aptixbot_plugin_aiocqhttp</small>
              <v-text-field label="仓库链接" v-model="extension_url" variant="outlined" required></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <h3>从本机上传 .zip 压缩包</h3>
            <v-col cols="12">
              <small>请保证插件文件存在压缩包根目录中的第一个文件夹中（即类似于从 GitHub 仓库页上下载的 Zip 压缩包的格式）。</small>
              <v-file-input label="选择文件" v-model="upload_file" accept=".zip" outlined required></v-file-input>
            </v-col>
          </v-row>
        </v-container>

        <br>
        <small>{{ status }}</small>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="dialog = false">
          关闭
        </v-btn>
        <v-btn color="blue-darken-1" variant="text" :loading="loading_" @click="newExtension()">
          安装
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="loadingDialog.show" width="700" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ loadingDialog.title }}</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-progress-linear indeterminate color="primary"
                v-if="loadingDialog.statusCode === 0"></v-progress-linear>
            </v-col>
          </v-row>
          <div class="py-12 text-center" v-if="loadingDialog.statusCode !== 0">
            <v-icon class="mb-6" color="success" icon="mdi-check-circle-outline" size="128"
              v-if="loadingDialog.statusCode === 1"></v-icon>
            <v-icon class="mb-6" color="error" icon="mdi-alert-circle-outline" size="128"
              v-if="loadingDialog.statusCode === 2"></v-icon>
            <div class="text-h4 font-weight-bold">{{ loadingDialog.result }}</div>
          </div>
          <div style="margin-top: 32px;">
            <h3>日志</h3>
            <ConsoleDisplayer historyNum="10" style="height: 200px; margin-top: 16px;"></ConsoleDisplayer>
          </div>

        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="resetLoadingDialog()">
          关闭
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="showPluginInfoDialog" width="1200">
    <template v-slot:activator="{ props }">
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ selectedPlugin.name }} 插件行为</span>
      </v-card-title>
      <v-card-text>
        <v-data-table style="font-size: 17px;" :headers="plugin_handler_info_headers" :items="selectedPlugin.handlers"
          item-key="name">
          <template v-slot:header.id="{ column }">
            <p style="font-weight: bold;">{{ column.title }}</p>
          </template>
          <template v-slot:item.event_type="{ item }">
            {{ item.event_type }}
          </template>
          <template v-slot:item.desc="{ item }">
            {{ item.desc }}
          </template>
          <template v-slot:item.type="{ item }">
            <v-chip color="success">
              {{ item.type }}
            </v-chip>
          </template>
          <template v-slot:item.cmd="{ item }">
            <span style="font-weight: bold;">{{ item.cmd }}</span>
          </template>
        </v-data-table>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="showPluginInfoDialog = false">
          关闭
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar :timeout="2000" elevation="24" :color="snack_success" v-model="snack_show">
    {{ snack_message }}
  </v-snackbar>

  <WaitingForRestart ref="wfr"></WaitingForRestart>
</template>

<script>

export default {
  name: 'ExtensionPage',
  components: {
    ExtensionCard,
    WaitingForRestart,
    ConsoleDisplayer,
    AptixBotConfig
  },
  data() {
    return {
      extension_data: {
        "data": [],
        "message": ""
      },
      extension_url: "",
      status: "",
      dialog: false,
      snack_message: "",
      snack_show: false,
      snack_success: "success",
      loading_: false,
      configDialog: false,
      extension_config: {
        "metadata": {},
        "config": {}
      },
      upload_file: null,
      pluginMarketData: {},
      loadingDialog: {
        show: false,
        title: "加载中...",
        statusCode: 0, // 0: loading, 1: success, 2: error,
        result: ""
      },

      announcement: "",
      showPluginInfoDialog: false,
      selectedPlugin: {},
      plugin_handler_info_headers: [
        { title: '行为类型', key: 'event_type_h' },
        { title: '描述', key: 'desc', maxWidth: '250px' },
        { title: '具体类型', key: 'type' },
        { title: '触发方式', key: 'cmd' },
      ],
      isListView: false,
      pluginMarketHeaders: [
        { title: '名称', value: 'name' },
        { title: '描述', value: 'desc' },
        { title: '作者', value: 'author' },
        { title: '操作', value: 'actions', sortable: false }
      ],
    }
  },
  mounted() {
    this.getExtensions();
    this.fetchPluginCollection();

    axios.get('https://api.Aptix.top/Aptixbot-announcement-plugin-market').then((res) => {
      let data = res.data.data;
      this.announcement = data.text;
    });
  },
  methods: {
    toast(message, success) {
      this.snack_message = message;
      this.snack_show = true;
      this.snack_success = success;
    },
    resetLoadingDialog() {
      this.loadingDialog = {
        show: false,
        title: "加载中...",
        statusCode: 0,
        result: ""
      }
    },
    onLoadingDialogResult(statusCode, result, timeToClose = 2000) {
      this.loadingDialog.statusCode = statusCode;
      this.loadingDialog.result = result;
      if (timeToClose === -1) {
        return
      }
      setTimeout(() => {
        this.resetLoadingDialog()
      }, timeToClose);
    },
    getExtensions() {
      axios.get('/api/plugin/get').then((res) => {
        this.extension_data = res.data;

        this.checkAlreadyInstalled();
      });
    },
    newExtension() {
      if (this.extension_url === "" && this.upload_file === null) {
        this.toast("请填写插件链接或上传插件文件", "error");
        return;
      }

      if (this.extension_url !== "" && this.upload_file !== null) {
        this.toast("请不要同时填写插件链接和上传插件文件", "error");
        return;
      }
      this.loading_ = true;
      this.loadingDialog.show = true;
      if (this.upload_file !== null) {
        this.toast("正在从文件安装插件", "primary");
        const formData = new FormData();
        formData.append('file', this.upload_file);
        axios.post('/api/plugin/install-upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }).then((res) => {
          this.loading_ = false;
          if (res.data.status === "error") {
            this.onLoadingDialogResult(2, res.data.message, -1);
            return;
          }
          this.extension_data = res.data;
          this.upload_file = "";
          this.onLoadingDialogResult(1, res.data.message);
          this.dialog = false;
          this.$refs.wfr.check();
        }).catch((err) => {
          this.loading_ = false;
          this.onLoadingDialogResult(2, err, -1);
        });
        return;
      } else {
        this.toast("正在从链接 " + this.extension_url + " 安装插件...", "primary");
        axios.post('/api/plugin/install',
          {
            url: this.extension_url
          }).then((res) => {
            this.loading_ = false;
            if (res.data.status === "error") {
              this.onLoadingDialogResult(2, res.data.message, -1);
              return;
            }
            this.extension_data = res.data;
            this.extension_url = "";
            this.onLoadingDialogResult(1, res.data.message);
            this.dialog = false;
            this.$refs.wfr.check();
          }).catch((err) => {
            this.loading_ = false;
            this.onLoadingDialogResult(2, err, -1);
          });

      }
    },
    uninstallExtension(extension_name) {
      this.toast("正在卸载" + extension_name, "primary");
      axios.post('/api/plugin/uninstall',
        {
          name: extension_name
        }).then((res) => {
          if (res.data.status === "error") {
            this.toast(res.data.message, "error");
            return;
          }
          this.extension_data = res.data;
          this.toast(res.data.message, "success");
          this.dialog = false;
          this.getExtensions();
        }).catch((err) => {
          this.toast(err, "error");
        });
    },
    updateExtension(extension_name) {
      this.loadingDialog.show = true;
      axios.post('/api/plugin/update',
        {
          name: extension_name
        }).then((res) => {
          if (res.data.status === "error") {
            this.onLoadingDialogResult(2, res.data.message, -1);
            return;
          }
          this.extension_data = res.data;
          console.log(this.extension_data);
          this.onLoadingDialogResult(1, res.data.message);
          this.dialog = false;
          this.$refs.wfr.check();
        }).catch((err) => {
          this.toast(err, "error");
        });
    },
    pluginOn(extension) {
      axios.post('/api/plugin/on',
        {
          name: extension.name
        }).then((res) => {
          if (res.data.status === "error") {
            this.toast(res.data.message, "error");
            return;
          }
          this.toast(res.data.message, "success");
          this.getExtensions();
        }).catch((err) => {
          this.toast(err, "error");
        });
    },
    pluginOff(extension) {
      axios.post('/api/plugin/off',
        {
          name: extension.name
        }).then((res) => {
          if (res.data.status === "error") {
            this.toast(res.data.message, "error");
            return;
          }
          this.toast(res.data.message, "success");
          this.getExtensions();
        }).catch((err) => {
          this.toast(err, "error");
        });
    },
    openExtensionConfig(extension_name) {
      this.curr_namespace = extension_name;
      this.configDialog = true;
      axios.get('/api/config/get?plugin_name=' + extension_name).then((res) => {
        this.extension_config = res.data.data;
        console.log(this.extension_config);
      }).catch((err) => {
        this.toast(err, "error");
      });
    },
    updateConfig() {
      axios.post('/api/config/plugin/update?plugin_name=' + this.curr_namespace, this.extension_config.config).then((res) => {
        if (res.data.status === "ok") {
          this.toast(res.data.message, "success");
          this.$refs.wfr.check();
        } else {
          this.toast(res.data.message, "error");
        }
      }).catch((err) => {
        this.toast(err, "error");
      });
    },
    fetchPluginCollection() {
      axios.get('/api/plugin/market_list').then((res) => {
        let data = []
        this.pluginMarketDataOrigin = res.data.data;
        for (let key in res.data.data) {
          data.push({
            "name": key,
            "desc": res.data.data[key].desc,
            "author": res.data.data[key].author,
            "repo": res.data.data[key].repo,
            "installed": false
          })
        }
        this.pluginMarketData = data;
        this.checkAlreadyInstalled();
      }).catch((err) => {
        this.toast("获取插件市场数据失败: " + err, "error");
      });
    },
    checkAlreadyInstalled() {
      for (let i = 0; i < this.pluginMarketData.length; i++) {
        this.pluginMarketData[i].installed = false;
      }
      for (let i = 0; i < this.pluginMarketData.length; i++) {
        for (let j = 0; j < this.extension_data.data.length; j++) {
          if (this.pluginMarketData[i].repo === this.extension_data.data[j].repo || this.pluginMarketData[i].name === this.extension_data.data[j].name) {
            this.pluginMarketData[i].installed = true;
          }
        }
      }

      // 将已安装的插件移动到最后面
      let installed = [];
      let notInstalled = [];
      for (let i = 0; i < this.pluginMarketData.length; i++) {
        if (this.pluginMarketData[i].installed) {
          installed.push(this.pluginMarketData[i]);
        } else {
          notInstalled.push(this.pluginMarketData[i]);
        }
      }
      this.pluginMarketData = notInstalled.concat(installed);
    },
    showPluginInfo(plugin) {
      this.selectedPlugin = plugin;
      this.showPluginInfoDialog = true;
    },
    reloadPlugin(plugin_name) {
      axios.post('/api/plugin/reload',
        {
          name: plugin_name
        }).then((res) => {
          if (res.data.status === "error") {
            this.onLoadingDialogResult(2, res.data.message, -1);
            return;
          }
          this.toast("重载成功", "success");
          this.getExtensions();
        }).catch((err) => {
          this.toast(err, "error");
        });
    }
  },
}

</script>