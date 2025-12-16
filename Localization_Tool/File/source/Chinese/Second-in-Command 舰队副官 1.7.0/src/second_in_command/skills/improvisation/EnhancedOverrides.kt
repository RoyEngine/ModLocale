package second_in_command.skills.improvisation

import com.fs.starfarer.api.campaign.CampaignFleetAPI
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.HullMods
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class EnhancedOverrides : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("安装有 \"安全协议超驰\" 船插的舰船获得以下增益: ", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - +25%% 性能峰值时间", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+25%")
        tooltip.addPara("   - +100 安全协议超驰 武器射程削减阈值", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+100")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        if (variant.hasHullMod(HullMods.SAFETYOVERRIDES)) {


            stats.peakCRDuration.modifyPercent(id, 25f)
            stats.weaponRangeThreshold.modifyFlat(id, 100f)

        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amunt: Float?) {

    }

    override fun onActivation(data: SCData) {

    }

    override fun onDeactivation(data: SCData) {

    }

    override fun getNPCSpawnWeight(fleet: CampaignFleetAPI): Float {
        if (fleet.fleetData.membersListCopy.any { it.variant.hasHullMod(HullMods.SAFETYOVERRIDES)}) return super.getNPCSpawnWeight(fleet)
        return 0f
    }


}