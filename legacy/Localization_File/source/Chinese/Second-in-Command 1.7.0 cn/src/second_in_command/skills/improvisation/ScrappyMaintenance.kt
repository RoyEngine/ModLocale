package second_in_command.skills.improvisation

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.ids.Tags
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ScrappyMaintenance : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("如果舰船在战斗中被击沉，有更大概率获得 D-插件", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("每拥有一个 D-插件 就 +3%% 战备值 (CR) 上限 (上限 5 D-插件)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("每拥有一个 D-插件 就 +5%% 战备值回复速度 (上限 5 D-插件)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        var dmods = 0

        var dmodSpecs = Global.getSettings().allHullModSpecs.filter { it.hasTag(Tags.HULLMOD_DMOD) }

        var hmods = variant.permaMods
        for (hmod in hmods) {
            if (dmodSpecs.map { it.id }.contains(hmod)) {
                dmods += 1
            }
        }

        dmods = dmods.coerceIn(0, 5)

        var cr = 0.03f * dmods
        var repairRate = 5f * dmods


        stats.maxCombatReadiness.modifyFlat(id, cr, "废料维护")
        stats.baseCRRecoveryRatePercentPerDay.modifyPercent(id, repairRate)
    }

    override fun callEffectsFromSeparateSkill(stats: MutableShipStatsAPI, hullSize: ShipAPI.HullSize, id: String) {
        stats.dynamic.getMod(Stats.DMOD_ACQUIRE_PROB_MOD).modifyMult(id, 1.5f)
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amunt: Float?) {

    }

    override fun onActivation(data: SCData) {

    }

    override fun onDeactivation(data: SCData) {

    }


}