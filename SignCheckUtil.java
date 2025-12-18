package org.jeecg.modules.aep.util;

import cn.hutool.crypto.digest.MD5;
import cn.hutool.json.JSONObject;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.stream.Collectors;


/**
 * 自定义验签工具
 *
 * @author Jiaxz
 * @date 2022年2月18日11:52:34
 */
@Component
public class SignCheckUtil {
    public static void main(String[] args) {
        JSONObject data = new JSONObject();
        data.put("appid","123");
        data.put("isIntegral","0");
        data.put("viewId","321");
        data.put("description","乱丢垃圾");

        String secret = "321";

        // 排序
        StringBuilder sb = new StringBuilder();
        List<String> sortingKeys = data.keySet().stream().sorted().collect(Collectors.toList());
        // 拼接 sign
        for (String key : sortingKeys) {
            String val = data.getStr(key);
            sb.append(key).append("=").append(val).append("&");
        }
        sb.deleteCharAt(sb.length() - 1);
        sb.append(secret);

        // 加密
        MD5 md5 = new MD5();
        String digestHex = md5.digestHex(sb.toString(), "UTF-8");
        digestHex = digestHex.toUpperCase();

        System.out.println("digestHex = " + digestHex);

        // 拼接 sign
        sb.append("sign=").append(digestHex);

        System.out.println("param = " + sb);
    }
    /**
     * 校验sign
     *
     * @param data   数据
     * @param secret 秘钥
     * @return true校验成功 false失败
     */
    public boolean checkSign(JSONObject data, String secret) {
        String sign = data.getStr("sign");
        data.remove("sign");

        StringBuilder sb = new StringBuilder();
        List<String> sortingKeys = data.keySet().stream().sorted().collect(Collectors.toList());
        for (String key : sortingKeys) {
            String val = data.getStr(key);
            sb.append(key).append("=").append(val).append("&");
        }
        sb.deleteCharAt(sb.length() - 1);
        sb.append(secret);

        MD5 md5 = new MD5();
        String digestHex = md5.digestHex(sb.toString(), "UTF-8");
        digestHex = digestHex.toUpperCase();

        return digestHex.equals(sign);
    }


}
