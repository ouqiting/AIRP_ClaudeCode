# PNG角色卡分离

SillyTavern 角色卡常以 PNG 文件分发，JSON 数据嵌入在图片的 `tEXt` 块中（keyword 为 `chara`），base64 编码。

## 分离步骤

```python
import struct, json, base64

def split_card(png_path):
    with open(png_path, 'rb') as f:
        data = f.read()

    # 扫描 PNG chunk
    pos = 8  # 跳过 PNG 签名
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8].decode('ascii', errors='replace')
        chunk_data = data[pos+8:pos+8+length]

        if chunk_type == 'tEXt':
            null_pos = chunk_data.find(b'\x00')
            keyword = chunk_data[:null_pos].decode('latin-1')
            text = chunk_data[null_pos+1:]
            if keyword == 'chara':
                card = json.loads(base64.b64decode(text))
                return card

        if chunk_type == 'IEND':
            break
        pos += 12 + length
    return None
```

## 输出

- JSON 数据（角色卡完整内容：name、description、personality、first_mes、scenario、世界书 等）
- 纯 PNG 图片（去掉 tEXt chunk 即可，体积通常缩小 70-90%）

## 使用

将 PNG 文件路径传入，即可提取内嵌的角色卡 JSON。生成两个产物：`xxx_extracted.json` + `xxx_pure.png`。
