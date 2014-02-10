#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#

import os
import subprocess
import sys
from xml.etree import ElementTree as etree
try:
    from graph import dep_graph, scm_deps
except ImportError:
    sys.exit("You must run bob-deps --graph --scm yourplans >graph.py")


def _url_from_plan(xml):
    "Extract the bob plan that this job builds."
    for builder in xml.find('builders'):
        if builder.tag != 'hudson.tasks.Shell':
            return None
        cmd = builder.find('command').text.split()
        if cmd[0].split('/')[-1] not in ('bob', 'bob-4.0', 'bob-jenkins', 'bob-jenkins-4.0'):
            continue
        for arg in cmd[1:]:
            if arg.endswith('.bob'):
                return arg
    return None


def _find_job(url):
    chunks = url.split('/')
    for n in range(len(chunks) - 1, -1, -1):
        path = '/'.join(chunks[n:])
        if os.path.exists(path):
            return path
    raise RuntimeError("Couldn't find %s in working directory" % url)


def main():
    top = 'jobs-clean'
    forest = 'scc/appengine'
    jobs = os.listdir(top)
    plan_to_job = {}
    job_to_plan = {}
    after = {}
    jobs_xml = {}
    to_write = set()
    for job in sorted(jobs):
        if not job.endswith('.xml'):
            continue
        with open(os.path.join(top, job)) as f:
            xml = etree.parse(f)
        url = _url_from_plan(xml)
        if not url:
            continue
        jobs_xml[job] = xml
        plan = os.path.basename(_find_job(url))
        plan_to_job[plan] = job
        job_to_plan[job] = plan
        for prov_plan in dep_graph[plan]:
            after.setdefault(job, set()).add(prov_plan)

    # dependencies
    for before_job, after_plans in after.iteritems():
        after_jobs = sorted(plan_to_job[x] for x in after_plans
                if x in plan_to_job)
        xml = jobs_xml[before_job]

        publishers = xml.find('publishers')
        children = set(x.rsplit('.', 1)[0] for x in after_jobs)
        for publisher in publishers.getchildren():
            if publisher.tag == 'hudson.tasks.BuildTrigger':
                children.update(publisher.find('childProjects').text.split(', '))
                publishers.remove(publisher)
        publisher = etree.SubElement(publishers, 'hudson.tasks.BuildTrigger')
        etree.SubElement(publisher, 'childProjects').text = ', '.join(sorted(children))
        threshold = etree.SubElement(publisher, 'threshold')
        etree.SubElement(threshold, 'name').text = 'SUCCESS'
        etree.SubElement(threshold, 'ordinal').text = '0'
        etree.SubElement(threshold, 'color').text = 'BLUE'
        etree.SubElement(threshold, 'completeBuild').text = 'true'

        to_write.add(before_job)

    # wms paths
    for job, xml in jobs_xml.items():
        plan = job_to_plan[job]
        paths = scm_deps.get(plan)
        if not paths:
            continue

        project = xml.getroot()
        scm = xml.find('scm')
        if scm is not None:
            project.remove(scm)
        scm = etree.SubElement(project, 'scm')
        scm.attrib['class'] = 'org.jenkinsci.plugins.git_wms.GitWMSAgent'
        etree.SubElement(scm, 'path').text = forest
        etree.SubElement(scm, 'branch').text = '@BRANCH@'
        watchPaths = etree.SubElement(scm, 'watchPaths')
        for url, path in paths:
            watchPath = etree.SubElement(watchPaths, 'org.jenkinsci.plugins.git__wms.GitWMSAgent_-WatchPath')
            etree.SubElement(watchPath, 'watchRepo').text = url
            etree.SubElement(watchPath, 'watchPath').text = path

        to_write.add(job)

    for job in to_write:
        xml = jobs_xml[job]
        out = os.path.join(top, job)
        with open(out + '.tmp', 'w') as f:
            p = subprocess.Popen(['tidy -i -xml -quiet -wrap 0'],
                    stdin=subprocess.PIPE, stdout=f, shell=True)
            p.communicate(etree.tostring(xml.getroot()))
            if p.wait():
                sys.exit("tidy failed")
        os.rename(out + '.tmp', out)

main()
