#format all txts to UTF-8/LF

1. using enca to convert files to UTF-8/LF, and use below check
	enca -L zh_CN -x UTF-8 */*.txt
	find -type f -name '*.txt' | xargs file
2. delete unneeded lines
	find -type f -name '*.txt' | xargs sed -i '/李敖研究网/d'
3. deleted trailing spaces
	find -type f -name '*.txt' | xargs sed -i 's/[ \t\r ]\+$//'
4. delete all spaces
	find -type f -name '*.md' | xargs sed -i 's/[  ]//'
5. rename all *.txt to *.md
	for f in *.txt; do mv -- "$f" "${f%.txt}.md"; done
