# -*- coding: utf-8 -*-

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(
        int('${version}'.split('.')[0]),
        int('${version}'.split('.')[1]),
        int('${version}'.split('.')[2]),
        0
    ),
    prodvers=(
        int('${version}'.split('.')[0]),
        int('${version}'.split('.')[1]),
        int('${version}'.split('.')[2]),
        0
    ),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', '${author}'),
        StringStruct('FileDescription', '${app_name}'),
        StringStruct('FileVersion', '${version}.0'),
        StringStruct('InternalName', '${app_name}'),
        StringStruct('LegalCopyright', '© ${author}. All rights reserved.'),
        StringStruct('OriginalFilename', '${app_name}.exe'),
        StringStruct('ProductName', '${app_name}'),
        StringStruct('ProductVersion', '${version}.0')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)