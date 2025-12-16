package second_in_command.skills.starfaring

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Expedition : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "技能"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+25%% 勘探废弃空间站等遗迹设施时获得的资源 - 不包括蓝图等稀有物品", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        //tooltip.addPara("+25%% resources - including rare items, such as blueprints - recovered from abandoned stations and derelicts", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+20%% 载货量 和 燃料容量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-20%% 燃料消耗", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-10%% 每月舰船维护消耗补给", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.suppliesPerMonth.modifyMult(id, 0.90f)
        stats!!.fuelUseMod.modifyMult(id, 0.80f)

        stats!!.cargoMod.modifyPercent(id, 20f)
        stats!!.fuelMod.modifyPercent(id, 20f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_expedition", 0.25f, "打捞作业")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).modifyFlat("sc_expedition", 0.25f, "打捞作业")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.SALVAGE_VALUE_MULT_FLEET_NOT_RARE).unmodify("sc_expedition")

    }

}