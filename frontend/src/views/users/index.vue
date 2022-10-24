<template>
  <div class="users-container">
    <el-tabs type="border-card" v-model="currentTab">
      <el-tab-pane label="用户管理" name="users">
        <div class="bar">
          <el-button @click="openDialog">创建用户</el-button>
        </div>
        <user-table :users="Users"/>
      </el-tab-pane>
    </el-tabs>
    <create-dialog/>
  </div>
</template>

<script>
import { getUsers } from "./api";
import UserTable from "./components/UserTable";
import CreateDialog from './components/CreateDialog'

export default {
  data() {
    return {
      currentTab: "users",
    };
  },
  created() {
    // getUsers(1).then(resp => {
    //   this.users = resp.data.users;
    // });
    this.$store.dispatch('GetUsers', {
      page: 1,
      pageSize: 10
    });
  },
  components: {
    UserTable,
    CreateDialog
  },
  methods: {
    openDialog() {
      this.$store.commit("CHANGE_USER_CREA_DIALOG", true);
    }
  },
  computed: {
    Users() {
      return this.$store.state.user.users
    }
  }
};
</script>

<style lang="scss">
.users-container {
  padding: 20px;
  .el-tabs {
    border: 0px;
    .el-tabs__header {
      background-color: $common_bg;
      border-bottom: 1px solid $common_bg;
      .el-tabs__nav-wrap {
        .el-tabs__nav-scroll {
          .el-tabs__nav {
            #tab-users {
              color: $active_color;
              background-color: $component_bg;
              border-top-left-radius: $radius;
              border-top-right-radius: $radius;
              border-right-color: $common_bg;
              border-left-color: $common_bg;
            }
          }
        }
      }
    }
    .el-tabs__content {
      padding: 15px;
      background-color: $component_bg;
    }
  }
  .bar {
    padding: 12px 0;
    .el-button {
      background-color: $dark_header;
      color: $font_color;
      border: none;
    }
  }
}
</style>

