#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
    forest = 'gerrit-pdt/appengine/appengine'
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
        for publisher in list(publishers.getchildren()):
            if publisher.tag == 'hudson.tasks.BuildTrigger':
                children.update(publisher.find('childProjects').text.split(','))
                publishers.remove(publisher)
            elif publisher.tag == 'hudson.plugins.descriptionsetter.DescriptionSetterPublisher':
                publishers.remove(publisher)

        publisher = etree.SubElement(publishers, 'hudson.plugins.descriptionsetter.DescriptionSetterPublisher')
        publisher.attrib['plugin'] = 'description-setter'
        etree.SubElement(publisher, 'regexp').text = 'Revisions built: (.*)'
        etree.SubElement(publisher, 'regexpForFailed')
        etree.SubElement(publisher, 'description').text = '\\1'
        etree.SubElement(publisher, 'setForMatrix').text = 'false'

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
        scm = etree.Element('scm')
        index = project.getchildren().index(project.find('properties')) + 1
        project.insert(index, scm)

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
            print >>f, "<?xml version='1.0' encoding='utf-8'?>"
            f.flush()
            p = subprocess.Popen(['tidy -config meta/tidy.conf'],
                    stdin=subprocess.PIPE, stdout=f, shell=True)
            xml.write(p.stdin)
            p.stdin.close()
            if p.wait():
                sys.exit("tidy failed")
        os.rename(out + '.tmp', out)

main()
