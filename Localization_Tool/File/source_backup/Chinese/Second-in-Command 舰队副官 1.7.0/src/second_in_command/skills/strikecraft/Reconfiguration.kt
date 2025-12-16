package second_in_command.skills.strikecraft

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.HullMods
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.misc.baseOrModSpec
import second_in_command.specs.SCBaseSkillPlugin

class Reconfiguration : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("消除 \"改装机库\" 船插的负面效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 只对基础部署点不低于 7 的舰船生效", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "7")

        tooltip.addSpacer(10f)

        tooltip.addPara("舰船插件：{改装机库 - 给非航母舰船提供临时甲板", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "改装机库")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        stats!!.dynamic.getMod(Stats.CONVERTED_HANGAR_NO_CREW_INCREASE).modifyFlat(id, 1f)
        stats!!.dynamic.getMod(Stats.CONVERTED_HANGAR_NO_REARM_INCREASE).modifyFlat(id, 1f)
        stats!!.dynamic.getMod(Stats.CONVERTED_HANGAR_NO_REFIT_PENALTY).modifyFlat(id, 1f)

        if (variant.baseOrModSpec().suppliesToRecover >= 7) {
            stats!!.dynamic.getMod(Stats.CONVERTED_HANGAR_NO_DP_INCREASE).modifyFlat(id, 1f)
        }


    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun applyEffectsToFighterSpawnedByShip(data: SCData, fighter: ShipAPI?, ship: ShipAPI?, id: String?) {

    }

    override fun onActivation(data: SCData) {

        var faction = Global.getSector().playerFaction
        if (!faction.knownHullMods.contains(HullMods.CONVERTED_HANGAR)) {
            faction.addKnownHullMod(HullMods.CONVERTED_HANGAR)
        }

    }

}