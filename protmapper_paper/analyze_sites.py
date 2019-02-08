import csv
import sys
import pickle
import matplotlib
matplotlib.use('agg')
import seaborn as sns
from matplotlib import pyplot as plt
from indra.util import plot_formatting as pf


def create_site_csv(site_dict, mapping_results, csv_file):
    header = ['SOURCE', 'GENE_NAME', 'UP_ID', 'ERROR_CODE', 'VALID', 'ORIG_RES',
              'ORIG_POS', 'MAPPED_RES', 'MAPPED_POS', 'DESCRIPTION',
              'SIDE', 'FREQ']
    all_sites = [header]
    for site in site_dict:
        ms = mapping_results[site]
        up_id, res, pos = site
        for side in ('lhs', 'rhs'):
            for source, stmts in site_dict[site][side].items():
                freq = len(stmts)
                if freq > 0:
                    row = [source, ms.gene_name, ms.up_id, ms.error_code,
                           ms.valid, ms.orig_res, ms.orig_pos, ms.mapped_res,
                           ms.mapped_pos, ms.description, side, freq]
                    all_sites.append(row)
    print("Saving %d entries to %s" % (len(all_sites)-1, csv_file))
    with open(csv_file, 'wt') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(all_sites)


def plot_site_stats(csv_file, output_base):
    site_df = pd.read_csv(csv_file)
    # Drop rows with error_code (invalid gene names in BEL)
    site_df = site_df[site_df.ERROR_CODE.isna()]
    results = print_stats(site_df)
    # Now make figures for the sites
    by_site = results[['Valid Sites', 'Mapped Sites', 'Unmapped Sites']]
    by_site_pct = results[['Valid Sites Pct.', 'Mapped Sites Pct. Total',
                           'Unmapped Sites Pct. Total']]
    by_occ = results[['Valid Occ.', 'Mapped Occ.', 'Unmapped Occ.']]
    by_occ_pct = results[['Valid Occ. Pct.', 'Mapped Occ. Pct. Total',
                          'Unmapped Occ. Pct. Total']]
    by_occ_corr = results[['Valid Occ.', 'Invalid Occ.']]
    by_occ_corr_pct = results[['Valid Occ. Pct.', 'Invalid Occ. Pct.']]

    for df, kind in ((by_site, 'by_site'), (by_site_pct, 'by_site_pct'),
                     (by_occ, 'by_occ'), (by_occ_pct, 'by_occ_pct')):
        plt.figure()
        df.plot(kind='bar', stacked=True, color=['blue', 'green', 'orange'])
        plt.subplots_adjust(bottom=0.2)
        plt.savefig('%s_%s.pdf' % (output_base, kind))
    for df, kind in ((by_occ_corr, 'by_occ_corr'),
                     (by_occ_corr_pct, 'by_occ_corr_pct')):
        plt.figure()
        df.plot(kind='bar', stacked=True, color=['blue', 'orange'])
        plt.subplots_adjust(bottom=0.2)
        plt.savefig('%s_%s.pdf' % (output_base, kind))


if __name__ == '__main__':
    # Create a single CSV file containing information about all sites from
    # databases
    if sys.argv[1] == 'create_site_csv':
        site_dict_file = sys.argv[2]
        mapping_results_file = sys.argv[3]
        csv_file = sys.argv[4]
        with open(site_dict_file, 'rb') as f:
            site_dict = pickle.load(f)
        with open(mapping_results_file, 'rb') as f:
            mapping_results = pickle.load(f)
        create_site_csv(site_dict, mapping_results, csv_file)
    # Load the CSV file and plot site statistics
    elif sys.argv[1] == 'plot_site_stats':
        input_file = sys.argv[2]
        output_base = sys.argv[3]
        plot_site_stats(input_file, output_file)
