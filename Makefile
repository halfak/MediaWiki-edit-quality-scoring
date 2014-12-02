datasets/treatment_sample_token_stats_0_600.tsv: \
		datasets/treatment_sample_revisions_0_600.txt
	cat datasets/treatment_sample_revisions_0_600.txt | \
	python token_stats.py --api=https://en.wikipedia.org/w/api.php > \
	datasets/treatment_sample_token_stats_0_600.tsv

datasets/treatment_sample_revision_stats_0_600.tsv: \
		datasets/treatment_sample_token_stats_0_600.tsv
	cat datasets/treatment_sample_token_stats_0_600.tsv | \
	python revision_stats.py > \
	datasets/treatment_sample_revision_stats_0_600.tsv

datasets/treatment_sample_token_stats_600_1200.tsv: \
		datasets/treatment_sample_revisions_600_1200.txt
	cat datasets/treatment_sample_revisions_600_1200.txt | \
	python token_stats.py --api=https://en.wikipedia.org/w/api.php > \
	datasets/treatment_sample_token_stats_600_1200.tsv

datasets/treatment_sample_revision_stats_600_1200.tsv: \
		datasets/treatment_sample_token_stats_600_1200.tsv
	cat datasets/treatment_sample_token_stats_600_1200.tsv | \
	python revision_stats.py > \
	datasets/treatment_sample_revision_stats_600_1200.tsv

datasets/treatment_sample_token_stats_1200_1900.tsv: \
		datasets/treatment_sample_revisions_1200_1900.txt
	cat datasets/treatment_sample_revisions_1200_1900.txt | \
	python token_stats.py --api=https://en.wikipedia.org/w/api.php > \
	datasets/treatment_sample_token_stats_1200_1900.tsv

datasets/treatment_sample_revision_stats_1200_1900.tsv: \
		datasets/treatment_sample_token_stats_1200_1900.tsv
	cat datasets/treatment_sample_token_stats_1200_1900.tsv | \
	python revision_stats.py > \
	datasets/treatment_sample_revision_stats_1200_1900.tsv
