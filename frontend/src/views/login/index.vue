<template>
  <div class="login-container">
    <vue-canvas-nest 
      :config="{color:'255,255,255', count: 300, opacity: 0.9}">
    </vue-canvas-nest>
    <el-form class="login-form" autoComplete="on" :model="loginForm" :rules="loginRules" ref="loginForm" label-position="left">
      <div class="logo-container">
        <svg-icon class="logo" icon="logo.1"/>
      </div>
      <h3 class="title">工业控制设备漏洞挖掘平台</h3>
      <el-form-item prop="username">
        <span class="svg-container svg-container_login">
        </span>
        <el-input name="username" type="text" v-model="loginForm.username" autoComplete="on" placeholder="username" />
      </el-form-item>
      <el-form-item prop="password">
        <span class="svg-container">
        </span>
        <el-input name="password" :type="pwdType" @keyup.enter.native="handleLogin" v-model="loginForm.password" autoComplete="on"
          placeholder="password"></el-input>
          <span class="show-pwd" @click="showPwd"><svg-icon icon="eye" /></span>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" style="width:100%;" :loading="loading" @click.native.prevent="handleLogin">
          登录
        </el-button>
      </el-form-item>
      <div class="tips">
        <span style="margin-right:20px;">版权所有</span>
        <div style="margin-left:80px;margin-top:-18px;"> 
            <div class="hdupng"></div>
            <div style="relative:position;margin-top:-24px;margin-left:35px;">杭州电子科技大学</div>
        </div>
        <div style="margin-left:80px;margin-top:20px;"> 
            <div class="companypng"></div>
            <div style="relative:position;margin-top:-24px;margin-left:35px;">浙江乾冠信息安全研究院有限公司</div>
        </div>
      </div>
    </el-form>
  </div>
</template>

<script>
import { isvalidUsername } from "@/utils/validate";
import vueCanvasNest from "vue-canvas-nest";
export default {
  components: {
    vueCanvasNest
  },
  name: "login",
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!isvalidUsername(value)) {
        callback(new Error("请输入正确的用户名"));
      } else {
        callback();
      }
    };
    const validatePass = (rule, value, callback) => {
      if (value.length < 2) {
        callback(new Error("密码不能小于5位"));
      } else {
        callback();
      }
    };
    return {
      loginForm: {
        username: "admin",
        password: "admin"
      },
      loginRules: {
        username: [
          { required: true, trigger: "blur", validator: validateUsername }
        ],
        password: [{ required: true, trigger: "blur", validator: validatePass }]
      },
      loading: false,
      pwdType: "password"
    };
  },
  methods: {
    showPwd() {
      if (this.pwdType === "password") {
        this.pwdType = "";
      } else {
        this.pwdType = "password";
      }
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true;
          this.$store
            .dispatch("Login", this.loginForm)
            .then(() => {
              this.loading = false;
              this.$router.push({ path: "/" });
            })
            .catch(err => {
              this.loading = false;
              let msg = err.response.data.msg;
              this.$message.error(msg)
            });
        } else {
          return false;
        }
      });
    }
  }
};
</script>


<style rel="stylesheet/scss" lang="scss">
$bg: #2d3a4b;
// $light_gray:#eee;
$light_gray: #fff;

/* reset element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;
    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      &:-webkit-autofill {
        -webkit-box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: #fff !important;
      }
    }
  }
  .el-form-item {
    border: 1px solid rgba(178, 178, 178, 0.4);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }

}
</style>

<style rel="stylesheet/scss" lang="scss" scoped>
$bg: #000;
$dark_gray: #889aa4;
// $light_gray:#eee;
$light_gray: #009deb;

.login-container {
  position: fixed;
  height: 100%;
  width: 100%;
  background-color: $bg;
  background-image: url('../../assets/ics_zip.jpg');
  background-repeat: no-repeat;
  background-position: 50%;
  background-size: 100% auto;
  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: rgba(0,0,0,.8);
    z-index: -1;
  }
  .logo-container {
    animation: rotation 4s linear infinite;
    width: 140px;
    height: 140px;
    margin: 30px auto;
    .logo {
      color: white;
      height: 100%;
      width: 100%;
    }
    @keyframes rotation {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }
  }

  .login-form {
    position: absolute;
    left: 0;
    right: 0;
    width: 360px;
    padding: 35px 35px 15px 35px;
    margin: 140px auto;
  }
  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;
    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }
  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
    &_login {
      font-size: 20px;
    }
  }
  .title {
    width: 130%;
    font-size: 38px;
    font-weight: 400;
    color: $light_gray;
    margin: 0px auto 40px -15%;
    text-align: center;
    font-weight: bold;
  }
  .show-pwd { 
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }
    .hdupng{
      background-image:url('../../assets/hdu.jpeg'); 
      //块里面如果没有内容，也没有设定div块的width和height,那么div块的高度和宽度则默认为0，背景图片也就不会出现了。如果不设定div块的高度和宽度，则其大小默认为内容的大小
      position:relative;
      width:25px;
      height: 25px;;
      background-size:100%;
      z-index:2;

      
  }
  .companypng{
      background-image:url('../../assets/qianguan.jpeg'); 
      //块里面如果没有内容，也没有设定div块的width和height,那么div块的高度和宽度则默认为0，背景图片也就不会出现了。如果不设定div块的高度和宽度，则其大小默认为内容的大小
      position:relative;
      width:30px;
      height: 30px;;
      background-size:100%;
      z-index:2;
  }

}
</style>
