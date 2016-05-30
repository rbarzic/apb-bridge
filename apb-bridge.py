# A chisel generator for an APB bridge/mux

import json
import argparse

# The template for the main file
tpl_file="""
package Apbbridge

import Chisel._
import cde.{{Parameters, Field}}
import junctions._

class Apbbridge  extends Module {{
  implicit val p = Parameters.empty
  val io = new Bundle {{
{master_ios}

{slave_ios}
  }}

{decoding_fns}

{bridge_inst}
{bridge_connect}

{master_connect}
{slave_connect}

}}


class ApbbridgeTests(c: Apbbridge) extends Tester(c) {{
  step(1)
}}

object Apbbridge {{
  def main(args: Array[String]): Unit = {{
    val tutArgs = args.slice(1, args.length)
    chiselMainTest(tutArgs, () => Module(new Apbbridge())) {{
      c => new ApbbridgeTests(c) }}
  }}
}}
"""
# smaller templates for code snippets (see string.format in Python doc if you are not familiar
# with the format)
tpl_master_ios = "    val {m_name} = new HastiSlaveIO()\n"
tpl_slave_ios = "    val {s_name} = new PociIO()\n"

tpl_master_connect = "    bridge.io.in <> io.{m_name}\n"
tpl_slave_connect =  "    io.{s_name} <> apbbus.io.slaves({s_idx})\n"

tpl_decoding_fns = "    val {fn_name} = (addr: UInt) => addr ({addr_msb},{addr_lsb}) === UInt ({addr_val})\n"

tpl_bridge_inst = """
    val bridge = Module(new HastiToPociBridge)
    val apbbus = Module(new PociBus(Seq({fn_list})))
"""

tpl_bridge_connect = "    apbbus.io.master <> bridge.io.out"



#ml_ahb = av.AutoVivification()
#
#
#ml_ahb['masters'] = ['jtag','dmem','imem']
#
#ml_ahb['slaves']['codemem']['address_range'] = [31,28]
#ml_ahb['slaves']['codemem']['address_value'] = 0
#
#ml_ahb['slaves']['datamem']['address_range'] = [31,28]
#ml_ahb['slaves']['datamem']['address_value'] = 2
#
#
#
#print(json.dumps (ml_ahb,
#      sort_keys=True,
#      indent=4, separators=(',', ': ')))
#


def master_connect(spec):
    txt = ""

    d = dict()
    d['m_name'] = spec['master']
    txt += tpl_master_connect.format(**d)

    return txt

def slave_connect(spec):
    txt = ""
    for i,s in enumerate(spec['slaves'].keys()):
        d = dict()
        d['s_name'] = s
        d['s_idx']  = i
        txt += tpl_slave_connect.format(**d)
    return txt



def decoding_fns(spec):
    txt = ""
    for i,s in enumerate(spec['slaves'].keys()):
        d = dict()
        d['fn_name'] = s + "_afn"
        d['addr_msb'],d['addr_lsb']  = spec['slaves'][s]['address_range']
        d['addr_val']= spec['slaves'][s]['address_value']
        txt += tpl_decoding_fns.format(**d)
    return txt


def master_ios(spec):
    txt = ""
    d = dict()
    d['m_name'] = spec['master']
    txt += tpl_master_ios.format(**d)
    return txt

def slave_ios(spec):
    txt = ""
    for s in spec['slaves'].keys():
        d = dict()
        d['s_name'] = s
        txt += tpl_slave_ios.format(**d)
    return txt


def bridge_inst(spec):
    txt = ""
    d = dict()
    d['fn_list']= ','.join([s+"_afn" for s in spec['slaves'].keys()])

    txt += tpl_bridge_inst.format(**d)
    return txt

def bridge_connect(spec):
    return tpl_bridge_connect

def get_args():
    """
    Get command line arguments
    """

    parser = argparse.ArgumentParser(description="""
    A Chisel generator for POCI bridge/mux (AHB/APB bridge with APB mux)
    """)

    parser.add_argument('--json', action='store', dest='json',
                        help='JSON file for the configuartion of the interconnect')

    parser.add_argument('--outdir', action='store', dest='outdir',
                        help='Directory where to store the chisel file')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()




if __name__ == '__main__':

    args = get_args()
    apbbridge = None
    with open(args.json) as f:
        print "-I- Reading JSON file " + args.json
        apbbridge = json.load(f)

    d=dict()
    d['master_connect'] = master_connect(apbbridge)
    d['slave_connect']  = slave_connect(apbbridge)
    d['decoding_fns']   = decoding_fns(apbbridge)
    d['master_ios']      = master_ios(apbbridge)
    d['slave_ios']      = slave_ios(apbbridge)
    d['bridge_inst']      = bridge_inst(apbbridge)
    d['bridge_connect']      = bridge_connect(apbbridge)
    txt = tpl_file.format(**d)

    outfile_name = args.outdir + "/Apbbridge.scala"
    with open(outfile_name,'w') as f:
        f.write(txt)
