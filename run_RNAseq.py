#!/usr/bin/env python

__author__ = 'emre'
import iLoop_RNAseq_pipeline.initiate_project as ip
import iLoop_RNAseq_pipeline.matchmaker as mm
import iLoop_RNAseq_pipeline.master_qsub as mq
import argparse
import logging

parser = argparse.ArgumentParser(description='This script will run RNAseq pipeline. Only works on Computerome.')

parser.add_argument('-p', '--project-path', help='Path to project folder', default=None)
parser.add_argument('-r', '--read-path',
                    help='Path to reads folder(s). Can be suplied as comma separated string. All files under the path tree will be added.',
                    default=None)
parser.add_argument('-j', '--jobs', help='Comma separated list of jobs to run.', default=[])
parser.add_argument('-m', '--map-to-mask', help='Run a separate mapping pipeline to mask.', action='store_true', default=False)
parser.add_argument('-n', '--number-of-cores', help='Number of cores to assign to individual jobs', default='8')
parser.add_argument('-s', '--strain-code',
                    help='Code for the reference strain. Available strains and corresponding codes are on "RNAseq_pipeline_references.tsv".',
                    default=None)
args = parser.parse_args()


def main():
    project_path = ip.check_project_path(args.project_path)
    logging.basicConfig(filename='{}/RNAseq_pipeline.log'.format(project_path),
                        format='%(asctime)s %(levelname)s : %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info('\n-----\nRNAseq pipeline started\n----')
    if args.jobs != []:
        jobs = args.jobs.split(',')
    else:
        jobs = []
    logging.info('Registered jobs are: {}'.format(','.join([job for job in jobs])))
    defaults = ip.get_defaults()
    ref = ip.get_reference(strain_code=args.strain_code, project_path=project_path)
    reads, project_path = ip.set_project(project_path=project_path, read_path=args.read_path)
    groups = mm.find_groups(project_path=project_path, reads=reads)
    essentials = [defaults, ref, reads, project_path, groups]
    if not any(ess for ess in essentials if not ess):
        subs = mq.job_organizer(project_path=project_path,
                                groups=groups,
                                readtype='raw',
                                ref=ref,
                                defaults=defaults,
                                ppn=args.number_of_cores,
                                jobs=jobs,
                                map_to_mask=args.map_to_mask)
    else:
        logger.error('Something is missing: \n{}'.format(
            ', '.join([ess for ess in essentials if not ess])))

if __name__ == "__main__":
    main()
