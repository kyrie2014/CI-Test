# coding:utf-8
from xml.dom import minidom, Node
from os.path import *
import sys
import pandas as pd
import re
import os
import copy


class AutoProcessor(object):
    xml_path = r'\\shnas01\publicshared\BM\BM_AutoTest\AutoTest_Case'
    bug_path = r'\\shnas01\publicshared\BM\BM_AutoTest\AutoBugs\bm_bug.xlsx'

    def __init__(self, log_path=None, case_dir=None, flag=None):

        self.result_path = join(
            join(
                log_path,
                AutoProcessor.latest_log_dirs(log_path, flag)[0]
            ),
            r'testResult.xml'
        ) if log_path is not None else None
        self.xml_path = join(self.xml_path, case_dir)
        # print self.result_path

    def filter_bug(self):
        if exists(self.bug_path):
            return None

        # filter用例名字
        def filter(summary):
            result = re.findall(r'#([\S\s]*)#', summary)
            if len(result) > 0:
                return result[0]
            return None

        df = pd.DataFrame(pd.read_excel(self.bug_path))
        new_df = df.apply(lambda summary: map(filter, df['Summary']), axis=0)

        return new_df['Summary'].tolist()

    def comment_node(self, xml_name, cases):
        xml_file = join(self.xml_path, xml_name)
        doc = minidom.parse(xml_file).documentElement
        element = doc.getElementsByTagName('TestCase') + doc.getElementsByTagName('Test')
        for node in element:
            if node.getAttribute('name') in cases:
                comment = node.ownerDocument.createComment(node.toxml())
                node.parentNode.replaceChild(comment, node)
        with open(xml_file, 'wb') as file:
            file.write(doc.toxml())

    def uncomment_node(self, xml_name, cases):
        import re
        xml_file = join(self.xml_path, xml_name)
        content, flag = '', False
        pattern = re.compile(r'<!--[\S\s]*{}[\S\s]*'.format('|'.join(cases)))
        with open(xml_file, 'r') as file:
            for line in file:
                filter = pattern.findall(line)
                if filter:
                    if '-->' not in filter[-1]:
                        flag = True
                    line = re.sub('(<!)?--[>]?', '', line)
                if flag and '-->' in line:
                    line = line.replace('-->', '')
                content += line
        with open(xml_file, 'wb') as file:
            file.write(content)

    def uncomment_all_nodes(self):
        import re
        for _, _, files in os.walk(self.xml_path):
            for file in files:
                if '.xml' not in file or '_plan.xml' in file:
                    continue
                print 'File: ' + file
                xml_file = join(self.xml_path, file)
                content, is_modified = '', False
                with open(xml_file, 'r') as file:
                    for line in file:
                        if re.findall(r'(<!--\s?<)|(>\s?-->)', line):
                            print 'Modified: ' + line
                            line = re.sub('(<!)?--[>]?', '', line)
                            is_modified = True
                        content += line
                if is_modified:
                    with open(xml_file, 'wb') as file:
                        file.write(content)

    @staticmethod
    def latest_log_dirs(path, flag):
        return sorted(
            [
                (x, getctime(join(path, x)))
                for x in os.listdir(path)
                if (isdir(join(path, x)) and flag in x)
                ],
            key=lambda i: i[1]
        )[-1]

    def comment_and_create_tpm_bug(self):
        fail_cases = dict()
        doc = minidom.parse(self.result_path).documentElement
        # node = doc.getElementsByTagName('Summary')[-1]
        # ratio = node.getAttribute('firstRunPassRate').strip('%')
        # if int(ratio) <= 30:
        #     return fail_cases_list
        node = doc.getElementsByTagName('TestBuildInfo')[-1]
        node2 = doc.getElementsByTagName('BuildInfo')[-1]

        # 获取测试结果失败的用例名
        nodes = doc.getElementsByTagName('TestCase')
        for n in nodes:
            xml_file_name = ''
            ch_nodes = [ch for ch in n.childNodes if ch.nodeType == n.ELEMENT_NODE]
            instance = copy.copy(n)
            for _ in range(10):
                instance = instance.parentNode
                if instance.tagName == 'TestPackage':
                    xml_file_name = instance.getAttribute('appPackageName')
                    break

            if 'pyInitialize' in xml_file_name:
                continue

            if len(ch_nodes) > 1:
                for cn in ch_nodes:
                    if 'fail' == cn.getAttribute('result'):
                        fail_cases[cn.getAttribute('name')] = xml_file_name
            else:
                cn = ch_nodes[-1]
                if 'fail' == cn.getAttribute('result'):
                    fail_cases[n.getAttribute('name')] = xml_file_name
                    
        if fail_cases is None:
            return
            
        # self.comment_node(comment_cases)
        # 初始化bug信息
        from BugInfo import BugInfo, BugDescription
        bug_info = BugInfo()
        bug_desc = BugDescription(
            device= node.getAttribute('deviceID'),
            url   = node.getAttribute('pack-url'),
            hw    = node.getAttribute('product-hardware'),
            path  = node.getAttribute('sharedPath'),
            ver   = node2.getAttribute('build_display')
        )

        from HttpHelper import HttpHelper
        for case, xml_name in fail_cases.items():
            # 注释case
            self.comment_node(xml_name + '.xml', case)
            bug_desc_instance = copy.copy(bug_desc)
            bug_desc_instance.case_name = case + '@' + xml_name
            # 提交TPM bug
            # print bug_info.format_bug_info(bug_desc_instance)
            HttpHelper().put(bug_info.format_bug_info(bug_desc_instance))


def init_option():
    from optparse import OptionParser
    parser = OptionParser(
        usage='%prog -p [common|uncommon|reset] [case_directory] [sn]',
        description='common or uncommon cases, and file bugs.'
    )
    parser.add_option(
        '-p',
        '--param',
        dest='param',
        nargs=3,
        action='store',
        help='common or uncommon cases, and file bugs',
        metavar='PARAM'
    )
    (options, args) = parser.parse_args()
    return options.param if options.param else sys.exit()


if '__main__' == __name__:
    param, case_dir, sn = init_option()

    # param, sn = 'common', 'SC77311E10181120412'
    cases = dict()
    try:
        if param == 'common':
            print 'common specified node'
            path = os.getcwd().replace('testcases\ext', 'results')
            ap = AutoProcessor(path, case_dir, sn)
            ap.comment_and_create_tpm_bug()

        elif param == 'uncommon':
            print 'uncommon specified node'
            ap = AutoProcessor(case_dir=case_dir)
            closed_bugs = ap.filter_bug()
            if closed_bugs is not None:
                for bug in closed_bugs:
                    print 'Bug --> ' + bug
                    tmp = bug.split('@')
                    if tmp[1] not in bugs:
                        cases[tmp[1]] = [tmp[0]]
                    else:
                        cases[tmp[1]].append(tmp[0])
                for file, cases in cases.items():
                    ap.uncomment_node(file, cases)
            else:
                print 'Not found bug!'

        elif param == 'reset':
            print 'reset all common node'
            ap = AutoProcessor(case_dir=case_dir)
            ap.uncomment_all_nodes()

    except Exception, cause:
        print cause
    print 'Total test is pass'
