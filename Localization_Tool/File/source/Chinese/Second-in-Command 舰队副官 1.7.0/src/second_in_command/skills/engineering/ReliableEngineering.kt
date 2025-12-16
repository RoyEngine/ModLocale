package second_in_command.skills.engineering

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ReliableEngineering : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("你所有舰船如果在战斗中被击沉，将几乎总是可在战斗后将其打捞和修复", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 战斗结束后，免费修复 30%% 的船体结构和装甲损伤", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-25%% 每月舰船维护消耗补给", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.suppliesPerMonth.modifyMult(id, 0.75f)
        stats!!.dynamic.getMod(Stats.INSTA_REPAIR_FRACTION).modifyFlat(id, 0.30f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_reliable_engineering", 2f)
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_reliable_engineering", 2f)
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).unmodify("sc_reliable_engineering")
    }

}