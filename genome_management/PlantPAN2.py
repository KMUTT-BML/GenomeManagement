# Author: Nattawet Sriwichai
# Author-email: nattawet.sri@mail.kmutt.ac.th
# https://github.com/evolu-tion/GenomeManagement
# Copyright (c) 2016 Nattawet Sriwichai
# License: LICENSE.txt 

############################### Initial Configuration ###########################################

# Input files is promoter sequence (fasta format) 
file_promoter = "out/promoter.fa"

# Configuration tfbs on promoter properties
# 1) filltering similarity score in range [0.5-1.0]
# 2) filltering tfbs on plus strand
filltered_similar_cutoff = 1.0
filltered_strand = 'Yes'

# Output file including
# 1) path directory to save backup HTML file from PlantPAN v2.0
# 2) list of tfbs on promoter
# 3) CpG island position on promoter
# 4) filltered tfbs with criteria of tfbs on promoter
backup_file_path = "out/backup_promoter_analysis_PlantPAN/"
file_name_tfbs_on_promoter = 'out/tfbs_on_promoter.txt'
file_name_tfbs_on_promoter_CpG_island = 'out/tfbs_on_promoter_CpG_island.txt'
file_name_tfbs_on_promoter_filltered = 'out/tfbs_on_promoter_filltered_[sim='+str(filltered_similar_cutoff)+'_strand_'+filltered_strand+'].txt'

##################################################################################################





##################################### Python Main Program ########################################
import urllib.parse
import urllib.request
import re

def PlantPAN2(seq_name, sequence):
	table_data = []

	# Get data from web and backup it
	url = 'http://plantpan2.itps.ncku.edu.tw/promoter_results.php'
	user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
	values = {	"sequence": ">" + seq_name + "\n" + sequence,
				"motif": "database",
				"choose": "allspecies",
				"TFBSspecies[]": "Arabidopsis_thaliana",
				"promoter[]": "Tandem",
				"promoter[]": "CpNpG",
				"submit": "Search"
			}
	headers = { 'User-Agent' : user_agent }

	data = urllib.parse.urlencode(values)
	data = data.encode('ascii')
	req = urllib.request.Request(url, data, headers)


	with urllib.request.urlopen(req) as response:
		# write backup file
		html_text = response.read()
		output = open(backup_file_path+seq_name+".html",'wb')
		output.write(html_text)
		output.close()
		html_text = html_text.decode('ascii')
		CpG_island = html_text

		# Search tfbs information data
		pos = html_text.find('Pattern Search Results')
		pos2 = html_text.find('Begin site', pos)
		html_text = html_text[pos:pos2].replace('\t','')
		html_text = html_text.split('<table width="1100" border="0" cellspacing="0" cellpadding="0" align=\'center\'>')[1:]
		for each_TFBS in html_text:
			pos = each_TFBS.find('value=\'')+7
			TFBS_mapped_info = each_TFBS[pos:each_TFBS.find('\'', pos)]
			TFBS_mapped_info = TFBS_mapped_info.split(':')
			TFBS_id = TFBS_mapped_info[0]

			pos = each_TFBS.find('&nbsp;&nbsp;/&nbsp;&nbsp;') + 25
			if(pos > 24):
				TFBS_TF_Fam = each_TFBS[pos: each_TFBS.find('<',pos)].replace('&nbsp;','')

			pos = each_TFBS.find('Hit Sequence', pos) + 36
			if(pos == 35):
				pos = each_TFBS.find('Hit sequence', pos) + 36

			table_tfbs = each_TFBS[pos:each_TFBS.find('</table>', pos)]
			table_tfbs = table_tfbs.split('<tr>')

			for i in range(len(table_tfbs)):
				table_row = table_tfbs[i].split('<td align=\'center\'>')[1:]
				tfbs_pos = table_row[0][:table_row[0].find('<')]
				tfbs_strand = table_row[1][:table_row[1].find('<')]
				tfbs_similar_score = table_row[2][:table_row[2].find('<')]
				tfbs_hit_seq = table_row[3][:table_row[3].find('<')]
				# print(TFBS_id, TFBS_TF_Fam, tfbs_pos, tfbs_strand, tfbs_similar_score, tfbs_hit_seq, sep="\t")
				table_data.append([seq_name, TFBS_id, TFBS_TF_Fam, tfbs_pos, tfbs_strand, tfbs_similar_score, tfbs_hit_seq])
			# pos = html.find("Strand-p</strong>")

		#Find CpG island
		pos = CpG_island.find("Strand-p")+50
		if (pos >50):
			pos2 = CpG_island.find("</table>",pos)
			CpG_island = CpG_island[pos:pos2].replace("</td><td align='center'>","\t").replace("</td></tr>","").replace("<td align='center'>","").replace("\t\t","\t-\t")
			CpG_island=CpG_island.split("<tr>")
			for i in range(len(CpG_island)):
				CpG_island[i] = CpG_island[i].split('\t')
				for j in range(len(CpG_island[i])):
					# print(CpG_island[i][j])
					if (CpG_island[i][j] == '+' or CpG_island[i][j] == '-'):
						pass
					else:
						CpG_island[i][j] = float(CpG_island[i][j])
			# print(CpG_island)
		else:
			CpG_island = ""
		return [table_data, CpG_island]


# Run PlantPAN2.0 of all sequence in fasta file
f = open(file_name_tfbs_on_promoter, 'a')
f.write('Promoter_ID\tMatrix ID\tFamily\tPosition\tStrand\tSimilar Score\tHit Sequence\n')

f_filltered = open(file_name_tfbs_on_promoter_filltered, 'w')
f_filltered.write('Promoter_ID\tMatrix ID\tFamily\tPosition\tStrand\tSimilar Score\tHit Sequence\n')

f_CpG_island = open(file_name_tfbs_on_promoter_CpG_island, 'w')
f_CpG_island.write('Promoter_id\tBegin\tEnd\tLength\tGC freq\tCpG ratio\tAT skew\tCG skew\tStart-p\tStrand\tStrand-p\n')


fasta_file = open(file_promoter, 'r')
gene = fasta_file.read().split('>')[1:]
for i in range(len(gene)):
	gene[i] = gene[i].split('\n')
	gene[i][0] = gene[i][0].split('|')
	gene_name = gene[i][0][0]
	seq = gene[i][1]
	print(i, gene_name)
	table = PlantPAN2(gene_name, seq)
	for data in table[0]:
		for item in data:
			f.write(item+'\t')
		f.write('\n')
		if (float(data[5]) >= filltered_similar_cutoff and  data[4] == '+' ):
			for item in data:
				f_filltered.write(item+'\t')
			f_filltered.write('\n')
	if table[1] != "" :
		for cpg_data in table[1]:
			f_CpG_island.write(gene_name+'\t')
			for item in cpg_data:
				f_CpG_island.write(str(item)+'\t')
			f_CpG_island.write('\n')
f.close()
f_filltered.close()