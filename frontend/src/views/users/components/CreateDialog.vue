<template>
  <div class="create-dialog">
    <el-dialog
      title="创建用户"
      :visible.sync="canOpen"
      :modal="true"
      :close-on-click-modal="false"
      width="40%"
    >
      <el-form ref="form" :model="form" label-width="120px">
        <el-form-item label="用户名*">
          <el-input v-model="form.username"></el-input>
        </el-form-item>
        <el-form-item label="密码*">
          <el-input v-model="form.password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="再一次输入密码*">
          <el-input v-model="form.password2" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item label="用户权限*">
          <el-select v-model="form.role" placeholder="请选择用户权限">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="普通用户" value="normal"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="用户描述">
          <el-input type="textarea" :rows="4" v-model="form.description" placeholder="请输入任务描述"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">创建</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { createUser } from "../api";
import { getToken } from "@/utils/auth";

export default {
  data() {
    return {
      form: {
        username: "",
        password: "",
        password2: "", // 第二次输入的密码
        role: "",
        description: ""
      }
    };
  },
  computed: {
    canOpen: {
      get() {
        return this.$store.state.user.createDialog;
      },
      set(value) {
        this.$store.commit("CHANGE_USER_CREA_DIALOG", value);
      }
    }
  },
  methods: {
    checkForm() {
      if (this.form.name === "") {
        this.$message("请输入用户名");
        return false;
      }

      if (this.form.role.length == 0) {
        this.$message("请选择用户类型");
        return false;
      }
      return true;
    },
    create() {
      if (!this.checkForm()) {
        return;
      }
      createUser(getToken(), this.form)
        .then(response => {
          this.$store.dispatch("GetUsers", {
      page: 1,
      pageSize: 10
    });
          this.$message.success("创建任务成功！");
          this.$store.commit("CHANGE_USER_CREA_DIALOG", false);
        })
        .catch(err => {
          let data = err.response.data;
          this.$message.info(data.msg);
        });
    }
  }
};
</script>

<style>
</style>
