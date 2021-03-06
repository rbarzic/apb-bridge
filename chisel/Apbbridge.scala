
package Apbbridge

import Chisel._
import cde.{Parameters, Field}
import junctions._

class Apbbridge  extends Module {
  implicit val p = Parameters.empty
  val io = new Bundle {
    val ahbport = new HastiSlaveIO()


    val uart = new PociIO()
    val gpio = new PociIO()
    val cpuctrl = new PociIO()
    val timer = new PociIO()
    val intc = new PociIO()

  }

    val uart_afn = (addr: UInt) => addr (31,24) === UInt (241)
    val gpio_afn = (addr: UInt) => addr (31,24) === UInt (240)
    val cpuctrl_afn = (addr: UInt) => addr (31,24) === UInt (244)
    val timer_afn = (addr: UInt) => addr (31,24) === UInt (243)
    val intc_afn = (addr: UInt) => addr (31,24) === UInt (242)



    val bridge = Module(new HastiToPociBridge)
    val apbbus = Module(new PociBus(Seq(uart_afn,gpio_afn,cpuctrl_afn,timer_afn,intc_afn)))

    apbbus.io.master <> bridge.io.out

    bridge.io.in <> io.ahbport

    io.uart <> apbbus.io.slaves(0)
    io.gpio <> apbbus.io.slaves(1)
    io.cpuctrl <> apbbus.io.slaves(2)
    io.timer <> apbbus.io.slaves(3)
    io.intc <> apbbus.io.slaves(4)


}


class ApbbridgeTests(c: Apbbridge) extends Tester(c) {
  step(1)
}

object Apbbridge {
  def main(args: Array[String]): Unit = {
    val tutArgs = args.slice(1, args.length)
    chiselMainTest(tutArgs, () => Module(new Apbbridge())) {
      c => new ApbbridgeTests(c) }
  }
}
