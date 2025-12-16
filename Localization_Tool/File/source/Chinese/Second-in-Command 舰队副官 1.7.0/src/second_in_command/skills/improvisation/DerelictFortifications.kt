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

class DerelictFortifications : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("每拥有一个 D-插件 就 +10 伤害减免用装甲值 (上限 5 个 D-插件)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("每拥有一个 D-插件 就 +3%% 装甲和船体结构值 (上限 5 个 D-插件)", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("绝大部分 D-插件的负面效果削弱 25%%*", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("*该效果与其他同类效果{乘算}叠加", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "乘算")

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

        var bonus = 3f * dmods

        stats.armorBonus.modifyPercent(id, bonus)
        stats.hullBonus.modifyPercent(id, bonus)


        stats.dynamic.getStat(Stats.DMOD_EFFECT_MULT).modifyMult(id, 0.75f)
        Preservation.reapplyDmods(variant, hullSize, stats)
        stats!!.effectiveArmorBonus.modifyFlat(id, 10f * dmods)

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