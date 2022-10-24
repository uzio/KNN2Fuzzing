<template>
  <div class="users-table">
    <el-table :data="users" :default-sort="{order: 'descending', prop: 'time'}">
      <el-table-column prop="username" label="用户名" width="300" :show-overflow-tooltip="true"></el-table-column>
      <el-table-column prop="role" label="权限" width="100"></el-table-column>
      <el-table-column prop="time" label="创建时间" width="150">
        <template slot-scope="scope">{{ formatDate(scope.row) }}</template>
      </el-table-column>
      <el-table-column prop="description" label="用户描述" :show-overflow-tooltip="true"></el-table-column>
      <el-table-column label="操作" width="140">
        <template slot-scope="scope">
          <el-button @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import moment from "moment";
import { deleteUser } from "../api";
import { getToken } from "@/utils/auth";

export default {
  props: {
    users: {
      type: Array
    }
  },
  created() {
    moment.locale("zh-cn");
  },
  methods: {
    formatDate(row) {
      return moment(row).format("YYYY, MMMM Do")
    },
    handleDelete(row) {
      let username = row.username;
      let token = getToken();
      deleteUser(token, username)
        .then(resp => {
          let statusCode = resp.status;
          if (statusCode == 200) {
            this.$message.success("用户删除成功");
            this.$store.dispatch("GetUsers");
          }
        })
        .catch(err => {
          console.log(err)
          let data = err.response.data;
          this.$message.info(data.msg);
        });
    }
  }
};
</script>

<style lang="scss">
$--table-current-row-background-color: red;
.users-table {
  .el-table {
    &::before {
      background-color: $component_bg;
    }
    th {
      background-color: rgb(36, 35, 35);
      &.is-leaf {
        border-bottom: 0px;
        border-left: 2px solid #424242;
        &:first-child {
          border-left: 0px;
        }
      }
    }
    tr {
      background-color: #575757;
      color: $font_color;
    }
    tr:hover > td {
      background-color: $component_bg;
    }
    td {
      border-bottom: 1px solid #777575;
    }
    .el-table__body-wrapper {
      background-color: $component_bg;

      .el-table__empty-block {
        background-color: $component_bg;
      }
    }
  }
}
</style>

