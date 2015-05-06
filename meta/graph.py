# Map of plan files to SCM paths they consume
scm_deps = {'amiconfig.bob': set([('gerrit-pdt/appengine/amiconfig', '')]),
 'catalog-service.bob': set([('gerrit-pdt/appengine/catalog-service', '')]),
 'conary-policy.bob': set([('gerrit-pdt/appengine/conary-policy', '')]),
 'conary.bob': set([('gerrit-pdt/appengine/conary', '')]),
 'crest.bob': set([('gerrit-pdt/appengine/crest', '')]),
 'entsrv.bob': set([('gerrit-pdt/appengine/entsrv', '')]),
 'flex3p.bob': set([('gerrit-pdt/archive/flex3p', '')]),
 'flexlibs.bob': set([('gerrit-pdt/appengine/flexlibs', '')]),
 'group-devimage-appliance.bob': set([('gerrit-pdt/appengine/recipes',
                                       'centos-6n/devimage-custom'),
                                      ('gerrit-pdt/appengine/recipes',
                                       'centos-6n/group-devimage-appliance')]),
 'group-entsrv.bob': set([('gerrit-pdt/appengine/recipes',
                           'centos-6n/group-entsrv-appliance')]),
 'group-rbuilder.bob': set([('gerrit-pdt/appengine/recipes',
                             'centos-6n/group-rbuilder-dist')]),
 'group-rpath-packages.bob': set([('gerrit-pdt/appengine/recipes',
                                   'centos-6n/group-rpath-packages')]),
 'group-rpath-platform.bob': set([('gerrit-pdt/appengine/recipes',
                                   'centos-6n/group-rpath-platform')]),
 'group-rwbs-appliance.bob': set([('gerrit-pdt/appengine/recipes',
                                   'centos-6n/group-rwbs-appliance')]),
 'group-updateservice.bob': set([('gerrit-pdt/appengine/recipes',
                                  'centos-6n/group-updateservice-appliance')]),
 'job.bob': set([('gerrit-pdt/appengine/rpath-job', '')]),
 'jobmaster.bob': set([('gerrit-pdt/appengine/jobmaster', '')]),
 'jobslave.bob': set([('gerrit-pdt/appengine/jobslave', '')]),
 'mcp.bob': set([('gerrit-pdt/appengine/mcp', '')]),
 'mint-test.bob': set([('gerrit-pdt/appengine/mint', '')]),
 'mint.bob': set([('gerrit-pdt/appengine/mint', '')]),
 'models.bob': set([('gerrit-pdt/appengine/rpath-models', '')]),
 'proddef.bob': set([('gerrit-pdt/appengine/rpath-product-definition', '')]),
 'product-definition-devimage-infra.bob': set([('gerrit-pdt/appengine/recipes',
                                                'product-definitions/devimage/product-definition')]),
 'product-definition-devimage.bob': set([('gerrit-pdt/appengine/recipes',
                                          'product-definitions/devimage/product-definition')]),
 'product-definition-entsrv.bob': set([('gerrit-pdt/appengine/recipes',
                                        'product-definitions/entsrv/product-definition')]),
 'product-definition-rba-infra.bob': set([('gerrit-pdt/appengine/recipes',
                                           'product-definitions/rba/product-definition')]),
 'product-definition-rba-vapp.bob': set([('gerrit-pdt/appengine/recipes',
                                          'product-definitions/rba/product-definition')]),
 'product-definition-rba.bob': set([('gerrit-pdt/appengine/recipes',
                                     'product-definitions/rba/product-definition')]),
 'product-definition-rus-infra.bob': set([('gerrit-pdt/appengine/recipes',
                                           'product-definitions/rus/product-definition')]),
 'product-definition-rus.bob': set([('gerrit-pdt/appengine/recipes',
                                     'product-definitions/rus/product-definition')]),
 'product-definition-rwbs-infra.bob': set([('gerrit-pdt/appengine/recipes',
                                            'product-definitions/rwbs/product-definition')]),
 'product-definition-rwbs.bob': set([('gerrit-pdt/appengine/recipes',
                                      'product-definitions/rwbs/product-definition')]),
 'pyovf.bob': set([('gerrit-pdt/appengine/pyovf', '')]),
 'rbuild.bob': set([('gerrit-pdt/appengine/rbuild', '')]),
 'rbuilder-ui.bob': set([('gerrit-pdt/appengine/rbuilder-ui', '')]),
 'restlib.bob': set([('gerrit-pdt/appengine/restlib', '')]),
 'rmake.bob': set([('gerrit-pdt/appengine/rmake', '')]),
 'rmake3.bob': set([('gerrit-pdt/appengine/rmake3', '')]),
 'robj.bob': set([('gerrit-pdt/appengine/robj', '')]),
 'rpath-repeater.bob': set([('gerrit-pdt/appengine/rpath-repeater', '')]),
 'rpath-tools.bob': set([('gerrit-pdt/appengine/rpath-tools', '')]),
 'smartform.bob': set([('gerrit-pdt/appengine/smartform', '')]),
 'storage.bob': set([('gerrit-pdt/appengine/rpath-storage', '')]),
 'testutils.bob': set([('gerrit-pdt/appengine/testutils', '')]),
 'upsrv.bob': set([('gerrit-pdt/appengine/rbm', '')]),
 'xml_resources.bob': set([('gerrit-pdt/appengine/xml_resources', '')]),
 'xmllib.bob': set([('gerrit-pdt/appengine/rpath-xmllib', '')]),
 'xobj.bob': set([('gerrit-pdt/appengine/xobj', '')])}
# map of providers to the set of requirers
dep_graph = {'amiconfig.bob': set(['catalog-service.bob', 'group-rpath-packages.bob']),
 'catalog-service.bob': set(['mint.bob']),
 'conary-policy.bob': set(['conary.bob']),
 'conary.bob': set(['amiconfig.bob',
                    'flex3p.bob',
                    'group-rwbs-appliance.bob',
                    'models.bob',
                    'product-definition-devimage-infra.bob',
                    'product-definition-devimage.bob',
                    'product-definition-entsrv.bob',
                    'product-definition-rba-infra.bob',
                    'product-definition-rba-vapp.bob',
                    'product-definition-rba.bob',
                    'product-definition-rus-infra.bob',
                    'product-definition-rus.bob',
                    'product-definition-rwbs-infra.bob',
                    'product-definition-rwbs.bob',
                    'restlib.bob',
                    'rmake.bob',
                    'rmake3.bob',
                    'xml_resources.bob',
                    'xmllib.bob',
                    'xobj.bob']),
 'crest.bob': set(['mint.bob']),
 'entsrv.bob': set(['group-devimage-appliance.bob',
                    'group-entsrv.bob',
                    'group-rbuilder.bob']),
 'flex3p.bob': set(['flexlibs.bob']),
 'flexlibs.bob': set(['rbuilder-ui.bob']),
 'group-devimage-appliance.bob': set(),
 'group-entsrv.bob': set(),
 'group-rbuilder.bob': set(),
 'group-rpath-packages.bob': set(),
 'group-rpath-platform.bob': set(),
 'group-rwbs-appliance.bob': set(),
 'group-updateservice.bob': set(),
 'job.bob': set(['catalog-service.bob']),
 'jobmaster.bob': set(['group-rbuilder.bob']),
 'jobslave.bob': set(['catalog-service.bob']),
 'mcp.bob': set(['jobmaster.bob', 'mint.bob']),
 'mint-test.bob': set(),
 'mint.bob': set(['entsrv.bob', 'group-updateservice.bob', 'mint-test.bob']),
 'models.bob': set(['catalog-service.bob', 'rpath-tools.bob']),
 'proddef.bob': set(['jobslave.bob', 'rbuild.bob']),
 'product-definition-devimage-infra.bob': set(),
 'product-definition-devimage.bob': set(),
 'product-definition-entsrv.bob': set(),
 'product-definition-rba-infra.bob': set(),
 'product-definition-rba-vapp.bob': set(),
 'product-definition-rba.bob': set(),
 'product-definition-rus-infra.bob': set(),
 'product-definition-rus.bob': set(),
 'product-definition-rwbs-infra.bob': set(),
 'product-definition-rwbs.bob': set(),
 'pyovf.bob': set(['jobslave.bob']),
 'rbuild.bob': set(['entsrv.bob']),
 'rbuilder-ui.bob': set(['group-rbuilder.bob']),
 'restlib.bob': set(['crest.bob', 'jobmaster.bob', 'jobslave.bob']),
 'rmake.bob': set(['catalog-service.bob', 'mcp.bob', 'rbuild.bob']),
 'rmake3.bob': set(['rpath-repeater.bob', 'upsrv.bob']),
 'robj.bob': set(['mint.bob', 'rbuild.bob']),
 'rpath-repeater.bob': set(['catalog-service.bob']),
 'rpath-tools.bob': set(['group-devimage-appliance.bob',
                         'group-entsrv.bob',
                         'group-rbuilder.bob',
                         'group-rpath-packages.bob',
                         'group-updateservice.bob']),
 'smartform.bob': set(['flexlibs.bob',
                       'rbuild.bob',
                       'rpath-repeater.bob',
                       'rpath-tools.bob']),
 'storage.bob': set(['job.bob']),
 'testutils.bob': set(['conary.bob']),
 'upsrv.bob': set(['group-updateservice.bob']),
 'xml_resources.bob': set(['flexlibs.bob']),
 'xmllib.bob': set(['proddef.bob', 'storage.bob']),
 'xobj.bob': set(['crest.bob', 'pyovf.bob', 'robj.bob', 'smartform.bob'])}
