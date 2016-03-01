package Apbbridge

import Chisel._
import cde.{Parameters, Field}
import junctions._

class Apbbridge  extends Module {
  implicit val p = Parameters.empty
  val io = new Bundle {
    val ahbport = new HastiSlaveIO
    val uart = new PociIO
    val gpio = new PociIO
  }

  val gpio_afn = (addr: UInt) => addr (31,24) === UInt (0xF0)
  val uart_afn = (addr: UInt) => addr (31,24) === UInt (0xF1)


  val bridge = Module(new HastiToPociBridge)
  val apbbus = Module(new PociBus(Seq(gpio_afn, uart_afn)))

  apbbus.io.master <> bridge.io.out

  io.gpio <> apbbus.io.slaves(0)
  io.uart <> apbbus.io.slaves(1)
  bridge.io.in <> io.ahbport

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
