# 项目说明

## 所有权说明

**这个github帐号whatot并非原著者，whatot只是将wjm_tcy编著的大李敖全集进行格式化，没有其它额外加工。
所有权利由leeao与wjm_tcy保持，此处仅为传播与留存。**

**编著者介绍见同目录“wjm_tcy.md”**

## 建库本意

我看wjm_tcy花费很多时间对“大李敖全集”进行整合，但是使用的txt格式，并且文件内无格式，不便于阅读，于是就对成品txt进行格式化。
最终组成一个gitbook项目，可以通过gitbook转化成pdf、epub或者mobi，便于在各种设备上阅读。

我对作者的文章内容持保留态度，仅通过此项目减少编著的合集埋没的可能。

## 生成pdf、epub或者mobi

参考 https://help.gitbook.com/

## 文件处理流程

* using enca to convert files to UTF-8/LF
	``enca -L zh_CN -x UTF-8 */*.txt``
* check all the txt files's coding
	``find -type f -name '*.txt' | xargs file``
* delete unneeded lines
	``find -type f -name '*.txt' | xargs sed -i '/李敖研究网/d'``
* deleted trailing spaces
	``find -type f -name '*.txt' | xargs sed -i 's/[ \t\r ]\+$//'``
* delete all spaces
	``find -type f -name '*.md' | xargs sed -i 's/[  ]//'``
* rename all *.txt to *.md
	``for f in *.txt; do mv -- "$f" "${f%.txt}.md"; done``

