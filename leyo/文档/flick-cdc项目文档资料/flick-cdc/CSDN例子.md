# FlinkCDC同步MySQL数据到ElasticSearch

## 一、背景

随着公司的业务量越来越大，查询需求越来越复杂，MySQL已经不支持变化多样的复杂查询了。

于是，使用CDC捕获MySQL的数据变化，同步到ES中，进行数据的检索。

## 二、环境准备

### 1、创建ES索引

```json
PUT /course
{
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text"
      },
      "label": {
        "type": "text"
      },
      "content": {
        "type": "text"
      }
    }
  }
}
```

- 查询course下所有数据（备用）：`GET /course/_search`
- 删除索引及数据（备用）：`DELETE /course`

### 2、创建MySQL数据表

```sql
CREATE TABLE `course` (
  `id` varchar(32) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## 三、使用FlinkCDC同步数据

### 1、导包

```xml
<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-clients</artifactId>
    <version>1.18.0</version>
</dependency>

<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-streaming-java</artifactId>
    <version>1.18.0</version>
</dependency>

<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-connector-base</artifactId>
    <version>1.18.0</version>
</dependency>

<dependency>
    <groupId>com.ververica</groupId>
    <artifactId>flink-connector-mysql-cdc</artifactId>
    <version>3.0.0</version>
</dependency>

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.27</version>
</dependency>

<dependency>
    <groupId>org.apache.flink</groupId>
    <artifactId>flink-table-runtime</artifactId>
    <version>1.18.0</version>
</dependency>
```

### 2、Demo

#### CDCTest.java

```java
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.ververica.cdc.connectors.mysql.source.MySqlSource;
import com.ververica.cdc.debezium.JsonDebeziumDeserializationSchema;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;

/**
 * CDC测试
 */
public class CDCTest {
    public static void main(String[] args) throws Exception {
        MySqlSource<String> mySqlSource = MySqlSource.<String>builder()
                .hostname("192.168.56.10")
                .port(3306)
                .databaseList("mytest")
                .tableList("mytest.course")
                .username("root")
                .password("${MYSQL_PASSWORD}")
                .deserializer(new JsonDebeziumDeserializationSchema())
                .build();

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(3000);

        env
                .fromSource(mySqlSource, WatermarkStrategy.noWatermarks(), "MySQL Source")
                .setParallelism(1)
                .addSink(new RichSinkFunction<String>() {
                    private final static ElasticSearchUtil es = new ElasticSearchUtil("192.168.56.10");

                    @Override
                    public void invoke(String value, Context context) throws Exception {
                        super.invoke(value, context);
                        JSONObject jsonObject = JSON.parseObject(value);
                        DataInfo dataInfo = new DataInfo();
                        dataInfo.setOp(jsonObject.getString("op"));
                        dataInfo.setBefore(jsonObject.getJSONObject("before"));
                        dataInfo.setAfter(jsonObject.getJSONObject("after"));
                        dataInfo.setDb(jsonObject.getJSONObject("source").getString("db"));
                        dataInfo.setTable(jsonObject.getJSONObject("source").getString("table"));

                        if (dataInfo.getDb().equals("mytest") && dataInfo.getTable().equals("course")) {
                            String id = dataInfo.getAfter().get("id").toString();
                            if (dataInfo.getOp().equals("d")) {
                                es.deleteById("course", id);
                            } else {
                                es.put(dataInfo.getAfter(), "course", id);
                            }
                        }
                    }
                })
                .setParallelism(1);

        env.execute("Print MySQL Snapshot + Binlog");
    }
}
```

#### DataInfo.java

```java
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;

import java.util.Map;

/**
 * 收集的数据类型
 * @author cuixiangfei
 * @since 20234-03-20
 */
public class DataInfo {

    // 操作 c是create；u是update；d是delete；r是read
    private String op;

    private String db;

    private String table;

    private Map<String, Object> before;

    private Map<String, Object> after;


    public String getOp() {
        return op;
    }

    public void setOp(String op) {
        this.op = op;
    }

    public String getDb() {
        return db;
    }

    public void setDb(String db) {
        this.db = db;
    }

    public String getTable() {
        return table;
    }

    public void setTable(String table) {
        this.table = table;
    }

    public Map<String, Object> getBefore() {
        return before;
    }

    public void setBefore(Map<String, Object> before) {
        this.before = before;
    }

    public Map<String, Object> getAfter() {
        return after;
    }

    public void setAfter(Map<String, Object> after) {
        this.after = after;
    }

    public boolean checkOpt() {
        if (this.op.equals("r")) {
            return false;
        }
        return true;
    }

    @Override
    public String toString() {
        return "DataInfo{" +
                "op='" + op + '\'' +
                ", db='" + db + '\'' +
                ", table='" + table + '\'' +
                ", before=" + before +
                ", after=" + after +
                '}';
    }

    public static void main(String[] args) {
        String value = "{\"before\":{\"id\":\"333\",\"name\":\"333\",\"label\":\"333\",\"content\":\"3333\"},\"after\":{\"id\":\"333\",\"name\":\"33322\",\"label\":\"333\",\"content\":\"3333\"},\"source\":{\"version\":\"1.9.7.Final\",\"connector\":\"mysql\",\"name\":\"mysql_binlog_source\",\"ts_ms\":1710923957000,\"snapshot\":\"false\",\"db\":\"mytest\",\"sequence\":null,\"table\":\"course\",\"server_id\":1,\"gtid\":null,\"file\":\"mysql-bin.000008\",\"pos\":1318,\"row\":0,\"thread\":9,\"query\":null},\"op\":\"u\",\"ts_ms\":1710923957825,\"transaction\":null}";
        JSONObject jsonObject = JSON.parseObject(value);

        System.out.println(jsonObject.get("op"));
        System.out.println(jsonObject.get("before"));
        System.out.println(jsonObject.get("after"));
        System.out.println(jsonObject.getJSONObject("source").get("db"));
        System.out.println(jsonObject.getJSONObject("source").get("table"));
    }
}
```

### 3、ES工具类

参考：[springboot集成elasticSearch（附带工具类）]()

## 四、测试

### 1、先创建几条数据

```sql
INSERT INTO `mytest`.`course`(`id`, `name`, `label`, `content`) VALUES ('1', '11', '111', '1111');
INSERT INTO `mytest`.`course`(`id`, `name`, `label`, `content`) VALUES ('2', '22 33', '222 333', '2222 3333');
INSERT INTO `mytest`.`course`(`id`, `name`, `label`, `content`) VALUES ('3', '33 44', '33 444', '3333 4444');
```

### 2、启动CDC

### 3、查询ES

### 4、增删改几条数据进行测验

---

**版权声明**：本文为CSDN博主「秃了也弱了。」的原创文章，遵循CC 4.0 BY-SA版权协议，辗转附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/A_art_xiang/article/details/136877379
