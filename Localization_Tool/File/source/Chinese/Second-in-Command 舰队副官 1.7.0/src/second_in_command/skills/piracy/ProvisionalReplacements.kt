package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.DModManager
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ProvisionalReplacements : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        //tooltip.addPara("All ships are much more likely to be recoverable if lost in combat", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("战斗结束后，免费修复 30%% 的船体结构和装甲损伤", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("D-插件 带来的舰船恢复消耗减免也适用于舰船维护消耗", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 实质上，这意味着每个 D-插件 会使每月维护消耗减少 20%%", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "20%")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        /*var dmods = 0

        var dmodSpecs = Global.getSettings().allHullModSpecs.filter { it.hasTag(Tags.HULLMOD_DMOD) }

        var hmods = variant.permaMods
        for (hmod in hmods) {
            if (dmodSpecs.map { it.id }.contains(hmod)) {
                dmods += 1
            }
        }

        var bonus = 0.06f * dmods
        bonus = bonus.coerceIn(0f, 0.30f)

        stats!!.suppliesPerMonth.modifyMult(id, 1-bonus, "Provisional Replacements")*/

        var dmods = DModManager.getNumDMods(variant)

        var mult = 1f
        for (dmod in 0 until dmods) {
            mult *= 0.8f
        }
        stats!!.suppliesPerMonth.modifyMult(id, mult)

        stats!!.dynamic.getMod(Stats.INSTA_REPAIR_FRACTION).modifyFlat(id, 0.30f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {


    }

    override fun advance(data: SCData, amount: Float) {
        //data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_provisional_replacements", 1.5f)

    }

    override fun onActivation(data: SCData) {
        //data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).modifyFlat("sc_provisional_replacements", 1.5f)

    }

    override fun onDeactivation(data: SCData) {
        //data.fleet.stats.dynamic.getMod(Stats.SHIP_RECOVERY_MOD).unmodify("sc_provisional_replacements")

    }

}