<template>
  <div class="vuls-table-container">
    <div class="job-table">
      <el-table :data="vuls">
        <el-table-column prop="title" label="漏洞名称"></el-table-column>
        <el-table-column prop="公开日期" label="公开时间" width="220"></el-table-column>
        <el-table-column label="危险级别" width="200">
          <template slot-scope="scope" width="200" >
            <div :class="getLevel(scope.row['危害级别'])">
            {{ GetLevel(scope.row['危害级别']) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="200"></el-table-column>
        <el-table-column prop="漏洞类型" label="类型" width="200">
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button @click="handleView(scope.row)">查看</el-button>
            <el-button @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog title="详细信息" :visible.sync="showDialog" width="50%">
      <div class="vul-container">
        <h3 class="vulTitle">{{ vul.title }}</h3>
        <table class="specifyTable">
          <colgroup>
            <col id="label">
            <col id="descript">
          </colgroup>
          <tr>
            <td class="key">CVE</td>
            <td class="value">{{ vul['CVE ID'] }}</td>
          </tr>
          <tr>
            <td class="key">CNVD</td>
            <td class="value">{{ vul['CNVD-ID'] }}</td>
          </tr>
          <tr>
            <td class="key">公开日期</td>
            <td class="value">{{ vul['收录时间'] }}</td>
          </tr>
          <tr>
            <td class="key">评分</td>
            <td class="value">{{ vul.score }}</td>
          </tr>
          <tr>
            <td class="key">危险级别</td>
            <td class="value">{{ getLevel }}</td>
          </tr>
          <tr>
            <td class="key">漏洞详情</td>
            <td class="value">{{ vul['漏洞描述'] }}</td>
          </tr>
          <tr>
            <td class="key">解决方案</td>
            <td class="value">{{ vul['漏洞解决方案'] }}</td>
          </tr>
          <tr>
            <td class="key">补丁信息</td>
            <td class="value">{{ vul['厂商补丁'] }}</td>
          </tr>
          <tr>
            <td class="key">验证信息</td>
            <td class="value">{{ vul['验证信息'] }}</td>
          </tr>
          <tr>
            <td class="key">参考链接</td>
            <td class="value">{{ vul['参考链接'] }}</td>
          </tr>
        </table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { deleteVul } from '../api';

export default {
  props: {
    vuls: {
      type: Array
    }
  },
  data() {
    return {
      vul: {},
      showDialog: false,
      // levelToType: {
      //   高: "danger",
      //   中: "warning",
      //   低: "info"
      // }
    };
  },
  methods: {
    handleView(row) {
      this.vul = row;
      this.showDialog = true;
    },
    handleDelete(row) {
      let id = row._id;
      deleteVul(id).then(_ => {
        this.$message('删除成功');
        this.$store.dispatch("reloadVuls");
      })
    },
    GetLevel(level) {
      if (typeof level === 'undefined') return '低'
      return level[0]
    },
    getLevel(level) {
      const levels = {
        高: "level-high",
        中: "level-middle",
        低: "level-low"
      };
      console.log("*******"+level);
      // console.log(levels[level[0]]);
      return levels[level[0]];
    },

  },
  computed: {
    // getLevel() {
    //   if (typeof vul === 'undefined') return '低'
    //   if (vul['危害级别']) {
    //     return vul.level[0]
    //   }
    //   return '高'
    // }
  }
};
</script>

<style lang="scss">
$--table-current-row-background-color: red;
.vuls-table-container {
  .job-table {
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
  .el-dialog {
    background-color: #777575;
    .el-dialog__header {
      background-color: #393939;
      .el-dialog__title {
        color: $font_color;
      }
    }
    .el-dialog__body {
      color: $font_color;

      .vul-container {
        .vulTitle {
          text-align: center;
        }
        .specifyTable {
          width: 100%;
          margin-top: 10px;
          td {
            border-bottom: #000;
            padding: 23px 7px 2px 7px;
          }
        }
        #label {
          width: 15%;
        }
        .key {
          text-align: right;
          font-weight: 600;
        }
        .value {
          line-height: 130%;
        }
      }
    }
  }

.level-high { // 与上面的level搭配使用，用于描述背景颜色
  color: #fe3932;
}
.level-middle {
  color: #fc8921;

}
.level-low {
  color: #ffd800;
}


}
</style>

