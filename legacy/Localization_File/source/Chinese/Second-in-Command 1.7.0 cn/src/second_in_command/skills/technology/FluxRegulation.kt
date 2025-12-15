package second_in_command.skills.technology

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class FluxRegulation : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        /*tooltip.addPara("+5 maximum flux capacitors and vents for all loadouts", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - If this officer is unassigned, capacitors and vents over the limit are removed", 0f, Misc.getTextColor(), Misc.getHighlightColor())*/


        /*tooltip.addPara("Flux capacity from capacitors is increased by 20", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("Flux dissipation from vents is increased by 2", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())*/


        tooltip.addPara("+10%% 幅能耗散", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+10%% 幅能容量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("幅能寄存器和耗散通道提供更多的幅能容量和耗散", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   每点幅能寄存器额外 +10 幅能容量", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+10")
        tooltip.addPara("   每点耗散通道额外 +1 幅能耗散", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+1")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        var vents = stats!!.variant.numFluxVents
        var caps = stats!!.variant.numFluxCapacitors
        var fluxIncrease = 1f * vents
        var capsIncrease = 10f * caps

        stats.fluxDissipation.modifyFlat(id, fluxIncrease)
        stats.fluxCapacity.modifyFlat(id, capsIncrease)

        stats!!.fluxDissipation.modifyPercent(id, 10f)
        stats!!.fluxCapacity.modifyPercent(id, 10f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amount: Float) {
       /* data.commander.stats.maxVentsBonus.modifyFlat("sc_flux_regulation", 5f)
        data.commander.stats.maxCapacitorsBonus.modifyFlat("sc_flux_regulation", 5f)*/
    }

    override fun onDeactivation(data: SCData) {
        /*data.commander.stats.maxVentsBonus.unmodify("sc_flux_regulation")
        data.commander.stats.maxCapacitorsBonus.unmodify("sc_flux_regulation")*/

    }

}