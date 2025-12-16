package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Stockpile : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("-5%% 补给和燃料消耗", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 载货量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 燃料容量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.suppliesPerMonth.modifyMult(id, 0.95f)
        stats!!.fuelUseMod.modifyMult(id, 0.95f)

        stats!!.cargoMod.modifyPercent(id, 30f)
        stats!!.fuelMod.modifyPercent(id, 30f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

}