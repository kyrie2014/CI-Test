# --*- coding:utf-8 -*--
from xml.dom import minidom
import copy


class BugInfo(object):

    __bug_info = dict()

    def __init__(self):
        doc = minidom.parse('BugInfo.xml').documentElement
        element = doc.getElementsByTagName('info')
        for node in element:
            self.__bug_info[node.getAttribute('name')] = node.getAttribute('value')

    def format_bug_info(self, bug_desc):
        print 'bug_desc.case_name --> '+ bug_desc.case_name
        __tmp = copy.copy(self.__bug_info)
        __tmp['summary'] = __tmp['summary'].format(caseName=bug_desc.case_name)
        __tmp['build_display'] = __tmp['build_display'].format(caseName=bug_desc.version)
        __tmp['description'] = bug_desc.get_bug_desc()
        format_http_params = ''
        for key, val in __tmp.items():
            format_http_params += (key + '=' + val)
            format_http_params += ('&' if val is not None else '')
        return format_http_params

    # def parser_result(self, fail_cases):
    #     keys = ['deviceID', 'pack-url', 'product-hardware', 'sharedPath', 'build_display']
    #     bugs_desc, attr = dict(), dict()
    #     doc = minidom.parse(self.result_file).documentElement
    #     node = doc.getElementsByTagName('TestBuildInfo')[-1]
    #     node2 = doc.getElementsByTagName('BuildInfo')[-1]
    #
    #     for key in keys:
    #         attr[key] = node.getAttribute(key)
    #     attr['build_display'] = node2.getAttribute('build_display')
    #     for case in fail_cases:
    #         attr['casename'] = case
    #         bugs_desc[case] = attr
        # elements = doc.getElementsByTagName('TestCase')
        # num = 0
        # for element in elements:
        #     ch_elements = [ch for ch in element.childNodes if ch.nodeType == Node.ELEMENT_NODE]
        #     if len(ch_elements) > 1:
        #         for ce in ch_elements:
        #             tmp = copy.copy(attr)
        #             if 'fail' == ce.getAttribute('result'):
        #                 num += 1
        #                 case_name = ce.getAttribute('name')
        #                 # if case_name not in tmp:
        #                 tmp['casename'] = case_name
        #                 bugs_desc['bug%d' % num] = tmp
        #     else:
        #         ce = ch_elements[-1]
        #         tmp = copy.copy(attr)
        #         case_name = element.getAttribute('name')
        #         if 'fail' == ce.getAttribute('result'):
        #             num += 1
        #             # if case_name not in tmp:
        #             tmp['casename'] = case_name
        #             bugs_desc['bug%d' % num] = tmp
        # return bugs


class BugDescription(object):

    description = \
        '''[1.Hardware Version   ]: Hardware:{product-hardware}, Serial No.:{deviceID}\r\n
           [2.Project Build      ]: \r{pack-url}\r\n
           [3.Storage Card       ]: 16G KINGSTON\r\n
           [4.SIM Card           ]: China Unicom,China Mobile\r\n
           [5.Testing Location   ]: SHZX15\r\n
           [6.Testing Steps      ]: 1.flash and power on 2.BM AutoDaily Test\r\n
           [7.Expected Result    ]: Normal operations and functions, no assert or other abnormal issues.\r\n
           [8.Test Result        ]: {caseName} fail\r\n
           [9.Analysis           ]: No analysis\r\n
           [10.Logpath           ]: {sharedPath}\r\n
           [11.Logfile           ]: --------------------------------------------------------\r\n
       '''

    __bug_desc = {
        'deviceID': '',
        'pack-url': '',
        'product-hardware': '',
        'sharedPath': '',
        'build_display': '',
        'caseName': ''
    }

    def __init__(self, device='', url='', hw='', path='',ver='',cn=''):
        self.__bug_desc['deviceID'] = device
        self.__bug_desc['pack-url'] = url
        self.__bug_desc['product-hardware'] = hw
        self.__bug_desc['build_display'] = ver
        self.__bug_desc['sharedPath'] = path
        self.__bug_desc['caseName'] = cn

    @property
    def device_id(self):
        return self.__bug_desc['deviceID']

    @device_id.setter
    def device_id(self, device):
        self.__bug_desc['deviceID'] = device

    @property
    def pack_url(self):
        return self.__bug_desc['pack-url']

    @pack_url.setter
    def pack_url(self, url):
        self.__bug_desc['pack-url'] = url

    @property
    def hardware(self):
        return self.__bug_desc['product-hardware']

    @hardware.setter
    def hardware(self, hw):
        self.__bug_desc['product-hardware'] = hw

    @property
    def log_path(self):
        return self.__bug_desc['sharedPath']

    @log_path.setter
    def log_path(self, path):
        self.__bug_desc['sharedPath'] = path

    @property
    def version(self):
        return self.__bug_desc['build_display']

    @version.setter
    def version(self, ver):
        self.__bug_desc['build_display'] = ver

    @property
    def case_name(self):
        return self.__bug_desc['caseName']

    @case_name.setter
    def case_name(self, cn):
        self.__bug_desc['caseName'] = cn

    def get_bug_desc(self):
        return self.description.format(**self.__bug_desc)